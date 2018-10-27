#include <iostream>
#include <sstream>
#include "test.h"

using namespace std;

int main(int argc, char const *argv[])
{

    if(argc > 2) {
        string cmd = string(argv[1]);
        if("parsehex" == cmd) {
            if(argc != 3) {
                cout << "error: args error!" << endl;
                return -1;
            }
            string hex = string(argv[2]);
            cout << "ParseHex: " << ParseHex(hex) << endl;
            return 1;
        } else if("gethex" == cmd) {
            if(argc != 3) {
                cout << "error: args error!" << endl;
                return -1;
            }
            string content = string(argv[2]);
            cout << "Hex: " << HexStr(content) << endl << "string length: " << content.size() << endl;
            return 1;
        } else if("getmsg" == cmd) {
            if(argc != 3) {
                cout << "error: args error!" << endl;
                return -1;
            }
            string hex = string(argv[2]);
            string head = hex.substr(0,45);
            string version = hex.substr(45,4);
            string timestamp = hex.substr(49,8);
            string type = hex.substr(57,4);
            string txidlen = hex.substr(61,8);
            string txid = hex.substr(69,64);
            string voutid = hex.substr(133,4);

            cout << "Message Head: " << ParseHex(head) << endl
                << "Message version: " << ParseHex(version) << endl
                << "Message timestamp: " << ParseHex(timestamp) << endl
                << "Message type: " << ParseHex(type) << endl
                << "Message txid length: " << ParseHex(txidlen) << endl
                << "Message txid: " << ParseHex(txid) << endl
                << "Message voutid: " << ParseHex(voutid) << endl;
        } else cout << "unknown command! " << cmd << endl;
        return 0;
    }

    CData tdata;

    cin >> tdata.n;

    ostringstream os;
    boost::archive::binary_oarchive oa(os);
    oa << tdata;

    string content = os.str();
    string hex = HexStr(content.c_str(), content.c_str()+content.size());
    cout << "result:" << endl << content << endl << "0x" << hex << endl;

    cout << "ParseHex: " << ParseHex(hex) << endl;

    return 0;
}
