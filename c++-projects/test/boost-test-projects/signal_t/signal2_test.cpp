#include <boost/signals2.hpp>
using namespace boost::signals2;


#include <iostream>
using std::cout;
using std::endl;

void slots1()
{
    cout << "slot1 called" << endl;
}
void slots2()
{
    cout << "slot2 called" << endl;
}

template<int N>
class Slot
{
public:
    int operator()(int x){
        cout << "slot " << N << " called" << endl;
        return N * x;
    }
};

void signals2_test()
{
    signal<void()> sig;  //一个信号插槽对象
    sig.connect(&slots1);  //连接插槽1,&可要可不要
    connection c2=sig.connect(slots2, boost::signals2::at_front);  //signals2::at_front标志slots2先被调用
    sig();  //调用operator()，产生信号（事件），触发插槽调用
	cout << "******slots2 and slots1" << endl;
    sig.disconnect(slots1);  //断开插槽slots1
    sig();
	cout << "******disconnect s1" << endl;
    c2.disconnect();
    //shared_connection_block block(c2);  //暂时阻塞插槽
    //do something
    //block.unblock();  //解除阻塞
    sig();
	cout << "*******c2 disconnect" << endl;



    signal<int(int)> sig2;
    sig2.connect(2,Slot<5>());
    sig2.connect(1,Slot<15>());  //1代表插槽组号
    sig2.connect(3,Slot<35>());
    int result=*sig2(2);  //返回最后一个插槽的返回值
    cout <<"*******result is "  << result << endl;
    sig2.disconnect(1);  //断开插槽组的连接
    sig2(2);
	cout << "******sig2(2) after disconnect 1" << endl;
}

int main()
{
	signals2_test();
	return 0;
}
