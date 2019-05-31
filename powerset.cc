#include <iostream>

using namespace std;

int num;

void printArray(int *array, int n)
{
    for (auto i = n - 1; i >= 0; i--) {
        cout << array[i];
    }
    cout << endl;
}

void perm(int *arr, int k, int n, int v)
{
    if (0 >= n) {
        printArray(arr, num);
        return;
    }

    for (auto ii = v; ii <= k; ii++) {
        arr[n - 1] = ii;
        perm(arr, k, n - 1, ii + 1);
    }
}


int main()
{
    // Number of digits e.g. n=3 xxx, yyy
    num = 3;

    // Range of numbers e.g. (1...3)
    int k = 3;
    int *arr = (int*) malloc(sizeof(int) * num);
    for (auto m = 1; m <= k; m++)
        perm(arr, k, m, 1);
}

// this is a test commit for git rebase
