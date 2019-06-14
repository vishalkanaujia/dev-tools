#include <iostream>

using namespace std;

class cqueue {
    private:
        int *list;
        int front;
        int rear;
        int size;

    public:
        cqueue(int s_size):size(s_size)
    {
        list = new int[size];
        front = rear = 0;
    }

        ~cqueue()
        {
            delete list;
        }

        void qinsert(int n);
        int qdelete();
};

void cqueue::qinsert(int n)
{
    cout << "Trying Insert " << n << endl;
    rear = (rear + 1) % (this->size);

    if (0 == rear && front == 0) {
        cout << "queue is full" << endl;
        rear = (rear + this->size - 1) % (this->size);
        return;
    }
    cout << "Insert " << n << endl;
    list[rear] = n;
}

int cqueue::qdelete()
{
    if  (front == rear) {
        cout << "queue is empty" << endl;
        return -1;
    }

    front = (front + 1) % (this->size);
    return list[front];
}

int main()
{

    cqueue queue(3);

    for (auto i = 10; i <= 30; i += 10) {
        queue.qinsert(i);
    }

    for (auto i = 10; i <= 30; i += 10) {
        cout << queue.qdelete() << endl;
    }
}
