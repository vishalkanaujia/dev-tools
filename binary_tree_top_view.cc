/*
   struct node
   {
   int data;
   node* left;
   node* right;
   };

 */

#include <algorithm>
int lookup(map <int, int > &m,
        int item,
        int level,
        map <int, int> &lv,
        int v)
{
    //cout << "lookup " << "rank=" << item << "level=" << level << "value=" << v << endl;
    if (m.find(item) != m.end()) {
        if (lv.find(v) != lv.end()) {
            int old_val = m[item];
            int old_level = lv[old_val];
            if (level < old_level)
                return 0;
        }
        return 1;
    }
    return 0;
}

void top_view_int(node *root,
        map <int, int> &m,
        int rank,
        int &min,
        int &max,
        int level,
        map <int, int> &lv)
{
    if (root == NULL)
        return;

    //cout << "Traversing " << root->data << " rank= " << rank;
    lv[root->data] = level;

    if (0 == lookup(m, rank, level, lv, root->data)) {
        //v.push_back(rank);
        // cout << root->data;
        m[rank] = root->data;

        //cout << "rank " << rank;
        if (rank < min)
            min = rank;
        if (rank > max)
            max = rank;
    }

    top_view_int(root->left, m, rank + 1, min, max, level + 1, lv);
    top_view_int(root->right, m, rank - 1, min, max, level + 1, lv);
}

void top_view(node * root)
{
    int rank = 0;
    int min = 0;
    int max = 0;
    std::map<int, int> m;
    std::map<int, int> lv;

    top_view_int(root, m, rank, min, max, 1, lv);

    //cout << "min " << min << "max " << max;   

    for (int i = max; i >= min; i--) {
        cout << m[i] << " "; 
    }   
}
