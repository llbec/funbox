using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Convertor
{
    internal class GaussCancellation
    {
        public readonly int VARIABLE;
        public double[][] arr;
        public double[] result;
        public GaussCancellation(int number)
        {
            VARIABLE = number;
            arr = new double[VARIABLE][];
            result = new double[VARIABLE];
            for (int i = 0; i < VARIABLE; i++)
            {
                arr[i] = new double[VARIABLE];
            }
        }

        private int CancellationDown(int x, int y)
        {
            int i;
            double coefficient;
            if (x <= y || x < 1) return -1;
            coefficient = arr[x][y] / arr[y][y];
            for (i = y; i < VARIABLE; i++)
            {
                arr[x][i] = arr[x][i] - arr[y][i] * coefficient;
            }
            result[x] = result[x] - result[y] * coefficient;
            return 0;
        }

        private int CancellationUp(int x, int y)
        {
            int i;
            double coefficient;
            if (x >= y || x > VARIABLE - 2) return -1;
            coefficient = arr[x][y] / arr[y][y];
            for (i = y; i > x; i--)
            {
                arr[x][i] = arr[x][i] - arr[y][i] * coefficient;
            }
            result[x] = result[x] - result[y] * coefficient;
            return 0;
        }

        private int ToOne(int x)
        {
            //int i;
            if (arr[x][x] == 0) return result[x] == 0 ? 0 : -1;
            /*for (i = 0; i < VARIABLE; i++)
            {
                if (arr[x][i] != 0 && x != i) return -1;
            }*/
            result[x] = result[x] / arr[x][x];
            arr[x][x] = 1;
            return 0;
        }

        public int Gauss()
        {
            int x, y;
            for (y = 0; y < VARIABLE - 1; y++)
            {
                for (x = y + 1; x < VARIABLE; x++)
                {
                    if (CancellationDown(x, y) < 0) return -1;
                }
            }
            for (y = VARIABLE - 1; y > 0; y--)
            {
                for (x = y - 1; x >= 0; x--)
                {
                    if (CancellationUp(x, y) < 0) return -1;
                }
            }
            for (x = 0; x < VARIABLE; x++)
            {
                if (ToOne(x) < 0) return -1;
            }
            return 0;
        }
    }
}
