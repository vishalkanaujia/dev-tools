//#include <bits/stdc++.h>
#include <iostream>
#include <cmath>

using namespace std;

vector<string> split_string(string);

int findDigitsSum(int d) {
    int c = 0;
    int sum = 0;

    while (1) {
        if (sum > 100) {
            break;
        }
        if (d < 10) {
            // cout << "first if d= " << d << endl;
            sum = d;
            break;
        }

        while (d) {
            c = d % 10;
            d = d / 10;
            sum += c;
            // cout << "second d= " << d << "sum = " << sum << endl;
        }
        d = sum;
        sum = 0;
    }
    return sum;
}


int findNearestStart(int num)
{
    int numDigits = 0;
    while (num) {
        numDigits++;
        num = num / 10;
    }
    return numDigits;
}


bool verifyPerfectSquare(int num)
{
    int start;
    int neartestSquare = 1;

    if (num < 100) {
        neartestSquare = 2;
    } else {
        start = findNearestStart(num);

        float count = floor(start/2);
        while (count) {
            neartestSquare *= 10;
            count--;
        }
    }

    for (int i = neartestSquare; i <= (num / 2); i++) {
        if ((i * i) == num) {
            cout << "verifyPerfectSquare num= " << num << " i= " << i << endl;
            return true;
        }

        if ((i * i) > num)
            break;
    }
    return false;

}
// Complete the squares function below.
int squares(float a, float b) 
{
    int lastDigit = 0;
    int sum = 0;
    int answer = 0;

    for (int i = a; i <= b; i++) {
        lastDigit = i % 10;
        //cout << "lastDigit= " << lastDigit << endl;

        if (lastDigit != 0 && lastDigit != 4 &&
                lastDigit != 9 && lastDigit != 1 &&
                lastDigit != 6 && lastDigit != 5) {
            //cout << i << " is not a PSQ" << endl;
            continue;
        }


        sum = findDigitsSum(i);
        // cout << "num =" << i << "sum of digits= " << sum << endl;
        if (sum == 1 || sum == 4 || sum == 7 || sum == 9) {
            //cout << "Perfect square possible: " << i << endl;
            if (true == verifyPerfectSquare(i)) {
                ++answer;
                cout << "answer = " << answer << endl;
            }
        } else {
            // cout << "sum improper.." << i << " is not a PSQ" << endl;
        }
        lastDigit = 0;
        sum = 0;
    }
    return answer;
}

int main()
{
    int res;
    res  = squares(385793959, 712365911);
    //float sq = sqrt(15763530163289);
    //cout << sq << endl;
    //res  = squares(sq, sq + 2);
    cout << "res= " << res << endl;
}
