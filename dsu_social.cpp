#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <string>
#include <chrono>
#include <algorithm>
#include <unordered_set>
#include <set>

using namespace std;

// ================= OPTIMIZED DSU =================
class DSU
{
    vector<int> parent, rankv;

public:
    DSU(int n)
    {
        parent.resize(n + 1);
        rankv.resize(n + 1, 0);
        for (int i = 1; i <= n; i++)
            parent[i] = i;
    }

    int find(int x)
    {
        if (parent[x] != x)
            parent[x] = find(parent[x]);
        return parent[x];
    }

    void unionSet(int x, int y)
    {
        int rx = find(x), ry = find(y);
        if (rx == ry)
            return;

        if (rankv[rx] < rankv[ry])
            parent[rx] = ry;
        else if (rankv[rx] > rankv[ry])
            parent[ry] = rx;
        else
        {
            parent[ry] = rx;
            rankv[rx]++;
        }
    }
};

// ================= NAIVE DSU =================
class NaiveDSU
{
    vector<int> parent;

public:
    NaiveDSU(int n)
    {
        parent.resize(n + 1);
        for (int i = 1; i <= n; i++)
            parent[i] = i;
    }

    int find(int x)
    {
        while (parent[x] != x)
            x = parent[x];
        return x;
    }

    void unionSet(int x, int y)
    {
        int rx = find(x), ry = find(y);
        if (rx != ry)
            parent[ry] = rx;
    }
};

// ================= SPLIT CSV =================
vector<string> splitCSV(string line) {
    vector<string> result;
    string cur;
    bool inQuotes = false;

    for(char c : line) {
        if(c == '"') {
            inQuotes = !inQuotes;
        }
        else if(c == ',' && !inQuotes) {
            result.push_back(cur);
            cur.clear();
        }
        else {
            cur += c;
        }
    }
    result.push_back(cur);

    // Trim spaces
    for(string &s : result) {
        while(!s.empty() && s[0]==' ') s.erase(0,1);
        while(!s.empty() && s.back()==' ') s.pop_back();
    }

    return result;
}

// ================= MAIN =================
int main()
{

    ifstream file("students.csv");

    if (!file)
    {
        cout << "CSV file not found\n";
        return 0;
    }

    int maxNode = 0;
    vector<string> rows;
    unordered_set<int> studentsSet;
    set<pair<int,int>> friendEdges;
    map<int, set<int>> adjacency;

    map<string, map<int, int>> subjectGlobal;
    map<int, map<string, vector<int>>> studentHelp;
    map<int, int> friendCount;

    vector<string> subjects = {"PCP", "TFCS", "DMS", "DS"};

    string line;
    getline(file, line); // skip header

    // Read all rows first and find max node ID before DSU allocation
    while (getline(file, line)) {
        if (line.empty())
            continue;
        vector<string> t = splitCSV(line);
        if (t.empty())
            continue;
        rows.push_back(line);

        // max student
        if (t.size() > 0) {
            try {
                int student = stoi(t[0]);
                maxNode = max(maxNode, student);
            } catch (...) {}
        }

        // max friends
        if (t.size() > 1) {
            string friends = t[1];
            friends.erase(remove(friends.begin(), friends.end(), '"'), friends.end());
            stringstream ss(friends);
            int f;
            while (ss >> f) {
                maxNode = max(maxNode, f);
            }
        }

        // no helper IDs needed for DSU
    }

    if (maxNode == 0) {
        cout << "No valid student data found\n";
        return 0;
    }

    DSU dsu(maxNode);
    NaiveDSU naive(maxNode);

    auto start1 = chrono::high_resolution_clock::now();

    for (auto &raw : rows) {
        vector<string> t = splitCSV(raw);
        if (t.empty())
            continue;

        if (t.size() < 6)
            continue;

        int student;
        try {
            student = stoi(t[0]);
        } catch (...) {
            continue;
        }
        if (student < 1 || student > maxNode)
            continue;

        studentsSet.insert(student);

        string friends = t[1];
        friends.erase(remove(friends.begin(), friends.end(), '"'), friends.end());
        stringstream ss(friends);
        int f;
        while (ss >> f) {
            if (f >= 1 && f <= maxNode) {
                dsu.unionSet(student, f);
                naive.unionSet(student, f);
                studentsSet.insert(f);
                friendCount[student]++;
                friendCount[f]++;
                adjacency[student].insert(f);
                adjacency[f].insert(student);
                int a = min(student, f);
                int b = max(student, f);
                friendEdges.insert({a, b});
            }
        }

        for (int i = 0; i < 4; i++) {
            if (i + 2 < t.size() && t[2 + i] != "") {
                try {
                    int helper = stoi(t[2 + i]);
                    subjectGlobal[subjects[i]][helper]++;
                    studentHelp[student][subjects[i]].push_back(helper);
                } catch (...) {
                }
            }
        }
    }

    auto end1 = chrono::high_resolution_clock::now();

    // ================= COMMUNITIES =================
    map<int, vector<int>> communities;

    for (int student : studentsSet)
    {
        int root = dsu.find(student);
        communities[root].push_back(student);
    }

    cout << "\n===== COMMUNITIES =====\n";
    int cid = 1;

    for (auto &c : communities)
    {
        cout << "Community " << cid++ << ": ";
        for (int x : c.second)
            cout << x << " ";
        cout << "\n";
    }

    // ================= COMMUNITY SIZE RANKING =================
    cout << "\n===== COMMUNITY SIZE RANKING =====\n";
    vector<pair<int, int>> sizes;
    for (auto &c : communities)
    {
        if (c.second.size() > 1)
            sizes.push_back({(int)c.second.size(), c.first});
    }
    sort(sizes.rbegin(), sizes.rend());
    for (auto &p : sizes)
    {
        cout << "Community Root " << p.second << " -> Size: " << p.first << "\n";
    }
    if (!sizes.empty())
    {
        cout << "\nLargest Community -> Root " << sizes[0].second
             << " Size: " << sizes[0].first << "\n";
    }

    // ================= GLOBAL INFLUENCERS =================
    cout << "\n===== GLOBAL TOP INFLUENCERS =====\n";

    for (auto &sub : subjectGlobal)
    {

        int best = -1, cnt = 0;

        for (auto &p : sub.second)
        {
            if (p.second > cnt)
            {
                cnt = p.second;
                best = p.first;
            }
        }

        cout << sub.first << " -> Student " << best << " (" << cnt << ")\n";
    }

    // ================= INFLUENCER VS CONNECTIVITY =================
    cout << "\n===== INFLUENCER VS CONNECTIVITY =====\n";
    for (auto &sub : subjectGlobal)
    {
        cout << "\nSubject: " << sub.first << "\n";
        for (auto &p : sub.second)
        {
            int student = p.first;
            int influence = p.second;
            int friends = friendCount[student];
            cout << "Student " << student
                 << " -> Influence: " << influence
                 << ", Friends: " << friends;
            if (influence > friends)
                cout << " [High academic influence, low connectivity]";
            else if (friends > influence)
                cout << " [Socially strong, less academic impact]";
            cout << "\n";
        }
    }

    // ================= BRIDGE STUDENTS =================
    cout << "\n===== BRIDGE STUDENTS =====\n";
    for (auto &p : adjacency)
    {
        int student = p.first;
        set<int> neighborRoots;
        for (int neighbor : p.second)
        {
            neighborRoots.insert(dsu.find(neighbor));
        }
        if (neighborRoots.size() > 1)
        {
            cout << "Student " << student << " is a BRIDGE (connects "
                 << neighborRoots.size() << " groups)\n";
        }
    }

    // ================= FUTURE INFLUENCERS =================
    cout << "\n===== FUTURE INFLUENCERS =====\n";
    map<int, int> score;
    for (auto &sub : subjectGlobal)
    {
        for (auto &p : sub.second)
        {
            int student = p.first;
            int influence = p.second;
            score[student] += influence * 2;
        }
    }
    for (auto &p : friendCount)
    {
        score[p.first] += p.second;
    }

    vector<pair<int, int>> ranking;
    for (auto &p : score)
        ranking.push_back({p.second, p.first});
    sort(ranking.rbegin(), ranking.rend());

    for (int i = 0; i < min(5, (int)ranking.size()); i++)
    {
        cout << "Student " << ranking[i].second
             << " -> Score: " << ranking[i].first << "\n";
    }

    // ================= COMMUNITY-WISE INFLUENCERS =================
    cout << "\n===== COMMUNITY-WISE INFLUENCERS (FIXED) =====\n";

    map<int, map<string, map<int, int>>> communityInfluence;

    for (auto &c : communities)
    {
        int root = c.first;
        for (int student : c.second)
        {
            if (!studentHelp.count(student))
                continue;

            for (auto &sub : studentHelp[student])
            {
                string subject = sub.first;
                for (int helper : sub.second)
                {
                    if (dsu.find(helper) == root)
                    {
                        communityInfluence[root][subject][helper]++;
                    }
                }
            }
        }
    }

    for (auto &c : communityInfluence)
    {
        cout << "\nCommunity Root " << c.first << ":\n";
        for (auto &sub : c.second)
        {
            string subject = sub.first;
            int best = -1, cnt = 0;
            for (auto &p : sub.second)
            {
                if (p.second > cnt)
                {
                    cnt = p.second;
                    best = p.first;
                }
            }
            if (best != -1)
            {
                cout << subject << " -> Student " << best << " (" << cnt << ")\n";
            }
            else
            {
                cout << subject << " -> (no influencers)\n";
            }
        }
    }

    // ================= TIME COMPARISON =================
    auto start2 = chrono::high_resolution_clock::now();

    for (int student : studentsSet)
        naive.find(student);

    auto end2 = chrono::high_resolution_clock::now();

    chrono::duration<double> optTime = end1 - start1;
    chrono::duration<double> naiveTime = end2 - start2;

    // ================= EXPORT GRAPH =================
    ofstream graphFile("graph_edges.txt");
    for (auto &e : friendEdges)
    {
        graphFile << e.first << " " << e.second << "\n";
    }
    graphFile.close();
    cout << "\nGraph exported to graph_edges.txt (for visualization)\n";

    // Export interactive HTML graph viewer
    {
        set<int> nodes;
        for (auto &e : friendEdges) {
            nodes.insert(e.first);
            nodes.insert(e.second);
        }

        ofstream htmlFile("graph_view.html");
        htmlFile << "<!doctype html>\n";
        htmlFile << "<html><head><meta charset='utf-8'><title>Community Graph</title>\n";
        htmlFile << "<script type='text/javascript' src='https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js'></script>\n";
        htmlFile << "<link href='https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.css' rel='stylesheet' />\n";
        htmlFile << "<style>body{margin:0;padding:0;}#mynetwork{width:100vw;height:100vh;border:1px solid #ddd;}</style>\n";
        htmlFile << "</head><body><div id='mynetwork'></div><script>\n";

        htmlFile << "const nodes = new vis.DataSet([";
        bool first = true;
        for (int n : nodes) {
            if (!first) htmlFile << ",";
            first = false;
            htmlFile << "{" << "id:" << n << ",label:'" << n << "'}";
        }
        htmlFile << "]);\n";

        htmlFile << "const edges = new vis.DataSet([";
        first = true;
        for (auto &e : friendEdges) {
            if (!first) htmlFile << ",";
            first = false;
            htmlFile << "{" << "from:" << e.first << ",to:" << e.second << "}";
        }
        htmlFile << "]);\n";

        htmlFile << "const container = document.getElementById('mynetwork');\n";
        htmlFile << "const data = { nodes: nodes, edges: edges };\n";
        htmlFile << "const options = { nodes: { shape: 'dot', size: 14, color: '#5DA9E9' }, edges: { color: '#888' }, physics: { stabilization: true, barnesHut: { gravitationalConstant: -2000 } } };\n";
        htmlFile << "new vis.Network(container, data, options);\n";
        htmlFile << "</script></body></html>\n";
        htmlFile.close();
        cout << "Graph viewer exported to graph_view.html\n";
    }

    cout << "\n===== PERFORMANCE =====\n";
    cout << "Optimized DSU Time: " << optTime.count() << " sec\n";
    cout << "Naive DSU Time: " << naiveTime.count() << " sec\n";

    return 0;
}