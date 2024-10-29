#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <map>
#include <cmath>
#include <time.h>

struct Node {
    std::string type;
    double work;
    double strands;
    double maxStrands;
};

struct Mode {
    double period;
    double totalWork;
    double workTypeA;
    double workTypeB;
    int totalCPUs;
    int cpusTypeA;
    int cpusTypeB;
    double spanTypeA;
    double spanTypeB;
    std::pair<double, double> totalWorkRange;
    std::pair<double, double> workTypeARange;
    std::pair<double, double> workTypeBRange;
};

struct Task {
    std::string type;
    double totalSpan;
    double spanTypeA;
    double spanTypeB;
    std::pair<double, double> totalWork;
    std::pair<double, double> workTypeA;
    std::pair<double, double> workTypeB;
    std::pair<double, double> period;
    double elasticity;
    std::vector<Node> nodes;
    std::vector<Mode> modes;
};

struct TimedMode {
    timespec period;
    timespec totalWork;
    timespec workTypeA;
    timespec workTypeB;
    timespec spanTypeA;
    timespec spanTypeB;
    struct WorkRanges {
        timespec min;
        timespec max;
    };
    WorkRanges totalWorkRange;
    WorkRanges workTypeARange;
    WorkRanges workTypeBRange;
    int totalCPUs;
    int cpusTypeA;
    int cpusTypeB;
};

// Helper function to extract number from string like "123.45ms"
double extractNumber(const std::string& str) {
    std::string numStr;
    for (char c : str) {
        if ((c >= '0' && c <= '9') || c == '.' || c == '-')
            numStr += c;
    }
    return std::stod(numStr);
}

// Helper function to extract range values [min, max]
std::pair<double, double> extractRange(const std::string& str) {
    size_t start = str.find('[');
    size_t comma = str.find(',');
    size_t end = str.find(']');
    
    std::string min = str.substr(start + 1, comma - start - 1);
    std::string max = str.substr(comma + 1, end - comma - 1);
    
    return {extractNumber(min), extractNumber(max)};
}

// Helper function to convert milliseconds to timespec
timespec msToTimespec(double ms) {
    timespec ts;
    double seconds = std::floor(ms / 1000.0);
    double remaining_ms = ms - (seconds * 1000.0);
    
    ts.tv_sec = static_cast<time_t>(seconds);
    ts.tv_nsec = static_cast<long>(remaining_ms * 1000000); // Convert ms to nanoseconds
    
    return ts;
}

// Helper function to convert a work range to timespec range
std::pair<timespec, timespec> rangeToTimespec(const std::pair<double, double>& range) {
    return {msToTimespec(range.first), msToTimespec(range.second)};
}

std::vector<Task> parseFile(const std::string& filename) {
    std::vector<Task> tasks;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        throw std::runtime_error("Unable to open file: " + filename);
    }

    std::string line;
    Task currentTask;
    Node currentNode;
    Mode currentMode;
    
    enum ParsingState {
        NONE,
        TASK_INFO,
        NODES,
        MODES
    } state = NONE;

    double current_span_a = 0.0;
    double current_span_b = 0.0;

    while (std::getline(file, line)) {
        if (line.empty()) continue;

        // Remove carriage return if present
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }

        if (line.find("Task") == 0) {
            if (state != NONE) {
                tasks.push_back(currentTask);
                currentTask = Task();
            }
            state = TASK_INFO;
            continue;
        }
        else if (line.find("Modes:") == 0) {
            state = MODES;
        }
        else if (line.find("Span A") == 0){
            current_span_a = extractNumber(line);
        }
        else if (line.find("Span B") == 0){
            current_span_b = extractNumber(line);
        }
        else if (state == MODES) {
            if (line.find("    Period:") == 0) {
                currentMode.period = extractNumber(line);
            }
            else if (line.find("    Total Work:") == 0) {
                currentMode.totalWork = extractNumber(line);
            }
            else if (line.find("    Work Type A:") == 0) {
                currentMode.workTypeA = extractNumber(line);
            }
            else if (line.find("    Work Type B:") == 0) {
                currentMode.workTypeB = extractNumber(line);
            }
            else if (line.find("    Total CPUs:") == 0) {
                currentMode.totalCPUs = static_cast<int>(extractNumber(line));
            }
            else if (line.find("    CPUs Type A:") == 0) {
                currentMode.cpusTypeA = static_cast<int>(extractNumber(line));
            }
            else if (line.find("    CPUs Type B:") == 0) {
                currentMode.cpusTypeB = static_cast<int>(extractNumber(line));
                
                // Copy the spans and ranges from task level
                currentMode.spanTypeA = current_span_a;
                currentMode.spanTypeB = current_span_b;
                currentMode.totalWorkRange;
                currentMode.workTypeARange;
                currentMode.workTypeBRange;
                
                currentTask.modes.push_back(currentMode);
                currentMode = Mode();
            }
        }
        else {
            state = NONE;
        }
    }

    // Handle the last task if it exists
    if (state != NONE) {
        tasks.push_back(currentTask);
        currentTask = Task();
    }

    return tasks;
}

// Function to convert Mode to TimedMode
TimedMode convertModeToTimed(const Mode& mode) {
    TimedMode timedMode;
    
    // Convert all time values to timespec
    timedMode.period = msToTimespec(mode.period);
    timedMode.totalWork = msToTimespec(mode.totalWork);
    timedMode.workTypeA = msToTimespec(mode.workTypeA);
    timedMode.workTypeB = msToTimespec(mode.workTypeB);
    timedMode.spanTypeA = msToTimespec(mode.spanTypeA);
    timedMode.spanTypeB = msToTimespec(mode.spanTypeB);
    
    // Convert ranges
    auto totalWorkRange = rangeToTimespec(mode.totalWorkRange);
    timedMode.totalWorkRange = {totalWorkRange.first, totalWorkRange.second};
    
    auto workTypeARange = rangeToTimespec(mode.workTypeARange);
    timedMode.workTypeARange = {workTypeARange.first, workTypeARange.second};
    
    auto workTypeBRange = rangeToTimespec(mode.workTypeBRange);
    timedMode.workTypeBRange = {workTypeBRange.first, workTypeBRange.second};
    
    // Copy CPU counts
    timedMode.totalCPUs = mode.totalCPUs;
    timedMode.cpusTypeA = mode.cpusTypeA;
    timedMode.cpusTypeB = mode.cpusTypeB;
    
    return timedMode;
}

// Function to convert all modes in a task to TimedMode structures
std::vector<TimedMode> getTimedModes(const Task& task) {
    std::vector<TimedMode> timedModes;
    for (const auto& mode : task.modes) {
        timedModes.push_back(convertModeToTimed(mode));
    }
    return timedModes;
}

// Helper function to print timespec (for verification)
void printTimespec(const timespec& ts) {
    std::cout << ts.tv_sec << "s " << ts.tv_nsec << "ns";
}

// Helper function to print timespec range (for verification)
void printTimespanRange(const TimedMode::WorkRanges& range) {
    std::cout << "[";
    printTimespec(range.min);
    std::cout << " - ";
    printTimespec(range.max);
    std::cout << "]";
}

// Function to print raw mode data for verification
void printRawModeData(const std::vector<Task>& tasks) {
    for (size_t i = 0; i < tasks.size(); i++) {
        const Task& task = tasks[i];
        std::cout << "Task " << (i + 1) << ":\n";
        std::cout << "Type: " << task.type << "\n";
        
        std::cout << "\nModes (" << task.modes.size() << "):\n";
        for (size_t j = 0; j < task.modes.size(); j++) {
            const Mode& mode = task.modes[j];
            std::cout << "  Mode " << (j + 1) << ":\n";
            std::cout << "    Period: " << mode.period << "ms\n";
            std::cout << "    Total Work: " << mode.totalWork << "ms\n";
            std::cout << "    Work Type A: " << mode.workTypeA << "ms\n";
            std::cout << "    Work Type B: " << mode.workTypeB << "ms\n";
            std::cout << "    Total Work Range: [" << mode.totalWorkRange.first 
                     << ", " << mode.totalWorkRange.second << "]ms\n";
            std::cout << "    Work Type A Range: [" << mode.workTypeARange.first 
                     << ", " << mode.workTypeARange.second << "]ms\n";
            std::cout << "    Work Type B Range: [" << mode.workTypeBRange.first 
                     << ", " << mode.workTypeBRange.second << "]ms\n";
            std::cout << "    Span Type A: " << mode.spanTypeA << "ms\n";
            std::cout << "    Span Type B: " << mode.spanTypeB << "ms\n";
            std::cout << "    CPUs - Total: " << mode.totalCPUs 
                     << ", Type A: " << mode.cpusTypeA 
                     << ", Type B: " << mode.cpusTypeB << "\n\n";
        }
        std::cout << "----------------------------------------\n\n";
    }
}

// Function to verify the conversion (for debugging)
void printTimedModes(const std::vector<TimedMode>& timedModes) {
    for (size_t i = 0; i < timedModes.size(); i++) {
        const auto& mode = timedModes[i];
        std::cout << "Mode " << (i + 1) << ":\n";
        
        std::cout << "  Period: ";
        printTimespec(mode.period);
        std::cout << "\n";
        
        std::cout << "  Total Work: ";
        printTimespec(mode.totalWork);
        std::cout << "\n";
        
        std::cout << "  Work Type A: ";
        printTimespec(mode.workTypeA);
        std::cout << "\n";
        
        std::cout << "  Work Type B: ";
        printTimespec(mode.workTypeB);
        std::cout << "\n";
        
        std::cout << "  Span Type A: ";
        printTimespec(mode.spanTypeA);
        std::cout << "\n";
        
        std::cout << "  Span Type B: ";
        printTimespec(mode.spanTypeB);
        std::cout << "\n";
        
        std::cout << "  CPUs - Total: " << mode.totalCPUs 
                 << ", Type A: " << mode.cpusTypeA 
                 << ", Type B: " << mode.cpusTypeB << "\n\n";
    }
}