#include <iostream>
#include <cmath>
#include <limits>
#include <algorithm>
#include <cerrno>
#include <float.h>
#include <map>
#include <tuple>

#include "taskData.h"
#include "extract.hpp"

//structure for internal knapsack scheduler
struct task_mode {
	double cpuLoss;
	double gpuLoss;
	size_t cores;
	size_t sms;
};

//table for easy task info access
std::vector<std::vector<task_mode>> task_table;

TaskData * add_td (double elasticity_,  int num_modes_, timespec * work_, timespec * span_, timespec * period_, timespec * gpu_work_, timespec * gpu_span_, timespec * gpu_period_)
{

	return new TaskData(elasticity_, num_modes_, work_, span_, period_, gpu_work_, gpu_span_, gpu_period_);

}

class schedule_struct {

	private:
	
		std::vector<bool> tasks_changelist;
		std::vector<int> tasks_current_modes;

	public:

		void add_task(){

			tasks_changelist.push_back(false);
			tasks_current_modes.push_back(0);

		}

		void set_task_changelist(int i, bool j){

			tasks_changelist.at(i) = j;

		}

		void set_task_current_mode(int i, int j){

			tasks_current_modes.at(i) = j;

		}

		int get_current_mode(int i){

			return tasks_current_modes.at(i);

		}

		bool get_changeable(int i){

			return tasks_changelist.at(i);

		}

} schedule;

int num_tasks = 0;

//populate table
void add_task(double elasticity_,  int num_modes_, timespec * work_, timespec * span_, timespec * period_, timespec * gpu_work_, timespec * gpu_span_, timespec * gpu_period_){
	
	//add the task to the legacy schedule object, but also add to vector
	//to make the scheduler much easier to read and work with.
	auto taskData_object = add_td(elasticity_, num_modes_, work_, span_, period_, gpu_work_, gpu_span_, gpu_period_);

	task_table.push_back(std::vector<task_mode>());

	for (int j = 0; j < num_modes_; j++){

		task_mode item;
		item.cpuLoss = (1.0 / taskData_object->get_elasticity() * (std::pow(taskData_object->get_max_utilization() - (taskData_object->get_work(j) / taskData_object->get_period(j)), 2)));
		item.gpuLoss = 0;
		item.cores = taskData_object->get_CPUs(j);
		item.sms = taskData_object->get_GPUs(j);

		task_table.at(task_table.size() - 1).push_back(item);

	}

	num_tasks++;

	return;
}

//Implement scheduling algorithm
void do_schedule(size_t maxCPU){

	//dynamic programming table
	int N = task_table.size();
    std::vector<std::vector<std::vector<std::pair<double, double>>>> dp(N + 1, std::vector<std::vector<std::pair<double, double>>>(maxCPU + 1, std::vector<std::pair<double, double>>(maxSMS + 1, {100000, 100000})));
    std::map<std::tuple<int,int,int>, std::vector<int>> solutions;

	//Execute double knapsack algorithm
    for (size_t i = 1; i <= num_tasks; i++) {

        for (size_t w = 0; w <= maxCPU; w++) {

            for (size_t v = 0; v <= maxSMS; v++) {

                //invalid state
                dp[i][w][v] = {-1, -1};  
                
				//if the class we are considering is not allowed to switch modes
				//just treat it as though we did check it normally, and only allow
				//looking at the current mode.
				if (!(schedule.get_changeable(i - 1))){

						auto item = task_table.at(i - 1).at((schedule.get_current_mode(i - 1)));

						//if item fits in both sacks
						if ((w >= item.cores) && (v >= item.sms) && (dp[i - 1][w - item.cores][v - item.sms].first != -1)) {

							int newCPULoss = dp[i - 1][w - item.cores][v - item.sms].first - item.cpuLoss;
							int newGPULoss = dp[i - 1][w - item.cores][v - item.sms].second - item.gpuLoss;
							
							//if found solution is better, update
							if ((newCPULoss + newGPULoss) > (dp[i][w][v].first + dp[i][w][v].second)) {

								dp[i][w][v] = {newCPULoss, newGPULoss};

								solutions[{i, w, v}] = solutions[{i - 1, w - item.cores, v - item.sms}];
								solutions[{i, w, v}].push_back((schedule.get_current_mode(i - 1)));

							}
						}
					}

				else {

					//for each item in class
					for (size_t j = 0; j < task_table.at(i - 1).size(); j++) {

						auto item = task_table.at(i - 1).at(j);

						//if item fits in both sacks
						if ((w >= item.cores) && (v >= item.sms) && (dp[i - 1][w - item.cores][v - item.sms].first != -1)) {

							int newCPULoss = dp[i - 1][w - item.cores][v - item.sms].first - item.cpuLoss;
							int newGPULoss = dp[i - 1][w - item.cores][v - item.sms].second - item.gpuLoss;
							
							//if found solution is better, update
							if ((newCPULoss + newGPULoss) > (dp[i][w][v].first + dp[i][w][v].second)) {

								dp[i][w][v] = {newCPULoss, newGPULoss};

								solutions[{i, w, v}] = solutions[{i - 1, w - item.cores, v - item.sms}];
								solutions[{i, w, v}].push_back(j);

							}
						}
					}
				}
            }
        }
    }

    //return optimal solution
	auto result = solutions[{N, maxCPU, maxSMS}];

}

int main(int argc, char *argv[]){
    try {
        std::vector<Task> tasks = parseFile(std::string(argv[1]));
        
		// Process each task
        for (size_t i = 0; i < tasks.size(); i++) {
            std::cout << "Task " << (i + 1) << " Modes:\n";
            std::cout << "----------------------------------------\n";
            
            // Convert and get timed modes
            std::vector<TimedMode> timedModes = getTimedModes(tasks[i]);
            
            // Print for verification
            printTimedModes(timedModes);
            
            // The timedModes vector now contains all mode information in timespec format
            // You can use it for further processing
            
            std::cout << "----------------------------------------\n\n";
        }

    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }



    return 0;
}
