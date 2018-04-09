#include <boost/variant.hpp>
#include <iostream>

using namespace std;

class printer_visitor : public boost::static_visitor <void>
{
public:
    void operator ()(int i) const
    {
        std::cout << "int : " << i << "; size:" << sizeof(i) << std ::endl;
    }
 
    void operator ()(std:: string& s ) const
    {
        std::cout << "string : " << s << "; size:" << sizeof(s) << std ::endl;
    }
 
    void operator ()(double d) const
    {
        std::cout << "double : " << d << "; size:" << sizeof(d) << std ::endl;
    }

	void operator ()(unsigned int i) const
	{
		cout << "uint : " << i << "; size:" << sizeof(i) << endl;
	}
	/*template <typename T>
	void operator()(T& operand) const
    {
       // operand += operand;
		cout << operand << endl;
    }*/
};

class add_visitor : public boost::static_visitor <void>
{
public:
	template <typename T>
    void operator()(T& operand) const
    {
        operand += operand;
    }
};

typedef boost:: variant<int , std:: string, double, unsigned int > testv;

struct aaa{
	testv a;
	testv b;
};

void printVariant( testv v)
{
	boost::apply_visitor(printer_visitor(), v);
};

void multiply2V(testv & v)
{
	boost::apply_visitor(add_visitor(), v);
}

void func1(testv & v)
{
	multiply2V(v);
	printVariant(v);
}

int main()
{
	std::vector<testv> vlist;
	vlist.push_back(4);
	vlist.push_back("hello world!");
    vlist.push_back(1.2);
    vlist.push_back(0x80000000);

	for(testv & vtmp : vlist)
	{
		printVariant(vtmp);
		func1(vtmp);
	}

	return 0;
}

#if 0
int main()
{
	std::vector <boost:: variant<int , std:: string, double, unsigned int > > v;
	v.push_back(4);
	v.push_back("hello world!");
	v.push_back(1.2);
	v.push_back(0x80000000);
//	printer_visitor visitor;
//	std::for_each (v. begin(), v .end(), boost::apply_visitor (visitor));
//	printer_visitor visitor;
//	boost::apply_visitor (visitor, v[0]);
//	for_each(v.begin(), v.end(), boost::apply_visitor(visitor));
	boost::variant<int, string, double, unsigned int> v1;
	cout << sizeof(int) <<"; " << sizeof(string) << "; " << sizeof(double) << "; " << sizeof(unsigned int) << "; " << sizeof(v1) << endl;
	v1 = 4;
	cout << sizeof(v1) << endl;
	boost::apply_visitor(printer_visitor(), v1);
	v1 = 0x80000000;
	cout << sizeof(v1) << endl;
	boost::apply_visitor(printer_visitor(), v1);
	v1 = 0xf;
	cout << sizeof(v1) << endl;
	boost::apply_visitor(printer_visitor(), v1);
	v1 = "There is no upgrade path from previous versions of Bitcore Node due to the removal of the included Bitcoin Core software. By installing this version, you must resynchronize the indexes from scratch.";
    cout << sizeof(v1) << endl;
    boost::apply_visitor(printer_visitor(), v1);
	v1 = (double)2;
	cout << sizeof(v1) << endl;
	boost::apply_visitor(printer_visitor(), v1);
	boost::variant<int, string, double, unsigned int> v2;
	v2 = v1;
	v2 = "[Init]";
	boost::apply_visitor(printer_visitor(), v2);
	boost::apply_visitor(add_visitor(), v2);
	boost::apply_visitor(printer_visitor(), v2);
	boost::apply_visitor(add_visitor(), v2);
    boost::apply_visitor(printer_visitor(), v2);
	v1 = v2;
	if(v1 == v2)
	{
		cout << "==" << endl;
	}
	else
	{
		v1 = v2;
		boost::apply_visitor(printer_visitor(), v1);
	}
	struct aaa a;
	a.a = v[0];
	a.b = v[1];
	boost::apply_visitor(printer_visitor(), a.a);
	boost::apply_visitor(printer_visitor(), a.b);

	return 0;
}
#endif
