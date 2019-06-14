#include <iostream>

using namespace std;

void swap (int *x, int *y)
{
    cout << "swapping " << *x << "& " << *y << endl;
    int t = *x;
    *x = *y;
    *y = t;
}

class MinHeap {
    int hcapacity;
    int *hp;

    public:
    MinHeap(int a[], int size)
    {
        hp = a;
        hcapacity = size;

        for (int i = 0; i < (size - 1)/2; i++)
            MinHeapify(i);
    }

    int parent(int i) { return (i - 1)/2; }
    int left(int i) { return 2*i + 1; } 
    int right(int i) { return 2*i + 2; } 
    void MinHeapify(int i);
};

void MinHeap::MinHeapify(int i)
{

    int l = left(i);
    int r = right(i);

    cout << "Heapify on index " << i << " l="<< l <<" r="<< r << endl;
    if (i > hcapacity)
        return;

    int small = i;

    if (l < hcapacity && hp[l] < hp[small]) {
        small = l;
    }
    if (r < hcapacity && r < hp[small]) {
        small = r;
    }

    if (small != i) {
        swap(&hp[small], &hp[i]);
        MinHeapify(small);
    }
    return;
}

int main()
{
    int a[] = {3,8,2,7,5};
    MinHeap mh(a, 5);
    for (int i = 0; i < 5; i++)
        cout << a[i] << endl;
}
