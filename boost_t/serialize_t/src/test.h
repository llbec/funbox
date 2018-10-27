#ifndef BOOST_SERIALIZE_TEST_H
#define BOOST_SERIALIZE_TEST_H
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>

class CData
{
public:
    int n;

public:
    CData() : n(0) {}
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive& ar, const unsigned int version)
    {
        ar & n;
    }
};

template<typename T>
std::string HexStr(const T itbegin, const T itend, bool fSpaces=false)
{
    std::string rv;
    static const char hexmap[16] = { '0', '1', '2', '3', '4', '5', '6', '7',
                                     '8', '9', 'a', 'b', 'c', 'd', 'e', 'f' };
    rv.reserve((itend-itbegin)*3);
    for(T it = itbegin; it < itend; ++it)
    {
        unsigned char val = (unsigned char)(*it);
        if(fSpaces && it != itbegin)
            rv.push_back(' ');
        rv.push_back(hexmap[val>>4]);
        rv.push_back(hexmap[val&15]);
    }

    return rv;
}

template<typename T>
inline std::string HexStr(const T& vch, bool fSpaces=false)
{
    return HexStr(vch.begin(), vch.end(), fSpaces);
}

/*ascII to hex ,rapaid code and decode */
const signed char p_util_hexdigit[256] =
{ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  0,1,2,3,4,5,6,7,8,9,-1,-1,-1,-1,-1,-1,
  -1,0xa,0xb,0xc,0xd,0xe,0xf,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,0xa,0xb,0xc,0xd,0xe,0xf,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
  -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, };

signed char HexDigit(char c)
{
    return p_util_hexdigit[(unsigned char)c];
}

std::string ParseHex(const char* psz)
{
    std::vector<unsigned char> vch;
    while (true)
    {
        while (isspace(*psz))
            psz++;
        signed char c = HexDigit(*psz++);
        if (c == (signed char)-1)
            break;
        unsigned char n = (c << 4);
        c = HexDigit(*psz++);
        if (c == (signed char)-1)
            break;
        n |= c;
        vch.push_back(n);
    }
    std::string res;
    res.insert(res.begin(), vch.begin(), vch.end());
    return res;
}

std::string ParseHex(const std::string& str)
{
    return ParseHex(str.c_str());
}

int Hex2Int(const std::string& str)
{
    int r = 0;
    if(str.size() != 8) return 0;
    for(int i = 0; i < 8; i++)
    {
        //int pos = (i/2)*8 + (i%2==0?4:0);
        //[](int x) { return (x/2 *8)+[](int y){return y%2==0?4:0}(x)}(i);
        r |= ((int)HexDigit(*(str.begin()+i))) << [](int x) { return (x/2 *8)+[](int y){ return y%2==0?4:0; }(x); }(i);
    }
    return r;
}
int64_t Hex2Int64(const std::string& str)
{
    int r = 0;
    if(str.size() != 16) return 0;
    for(int i = 0; i < 16; i++)
    {
        //int pos = (i/2)*8 + (i%2==0?4:0);
        //[](int x) { return (x/2 *8)+[](int y){return y%2==0?4:0}(x)}(i);
        r |= ((int64_t)HexDigit(*(str.begin()+i))) << [](int x) { return (x/2 *8)+[](int y){ return y%2==0?4:0; }(x); }(i);
    }
    return r;
}
#endif
