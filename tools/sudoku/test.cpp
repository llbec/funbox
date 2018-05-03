#include "lib/sudoku_x.h"

class sudoku_9 : public Sudoku_X<3>
{
public:
    sudoku_9(){}
};

int main()
{
    sudoku_9 test;
    test.SetNull();
	test.Show();
    return 0;
}
