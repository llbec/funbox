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
            string head(argv[2], argv[2]+45);
            string version(argv[2]+45, argv[2]+49);
            string timestamp(argv[2]+49, argv[2]+57);
            string type(argv[2]+57, argv[2]+61);
            string txidlen(argv[2]+61, argv[2]+69);
            string txid(argv[2]+69, argv[2]+133);
            string voutid(argv[2]+133, argv[2]+137);
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
