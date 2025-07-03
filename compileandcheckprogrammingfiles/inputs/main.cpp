#include <iostream>
#include <vector>

int main() {
    // Hardcoded numbers
    std::vector<int> numbers = {10, 20, 30, 40, 50};

    int sum = 0;
    for (int n : numbers) {
        sum += n;
    }

    double average = static_cast<double>(sum) / numbers.size();

    std::cout << "The average is: " << average << std::endl;

    return 0;
}
