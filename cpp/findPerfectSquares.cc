#include <iostream>

using namespace std;

int findDigitsSum(int d)
{
    int c = 0;
    int sum = 0;

    while (d) {
        c = d % 10;
        d = d / 10;
        sum += c;
    }
    return sum;
}

// Complete the squares function below.
int squares(int a, int b) {
    int lastDigit = 0;
    int sum = 0;

    for (int i = a; i <= b; i++) {
        lastDigit = i % 10;
        if (lastDigit == 2 || lastDigit == 3 ||
                lastDigit == 7 || lastDigit == 8) {
            cout << i << " is not a PSQ" << endl;
            continue;
        }
        sum = findDigitsSum(i);
        cout  << "i =" << i << "sum= " << sum << endl;
        if (sum == 0 || sum == 1 || sum == 4 || sum == 7) {
            cout << "Perfect square: "<< i << endl;
        } else {
            cout << "sum improper.." << i << " is not a PSQ" << endl;
        }
        lastDigit = 0;
        sum = 0;
    }
    return 0;
}

int main()
{
    int s = squares(1, 5);
    cout << "s= " << s << endl;
}
