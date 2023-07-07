using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Convertor
{
    public partial class Form1 : Form
    {
        private double slope = 1, offset = 0;
        private double A = 0, B = 0, C = 0, D = 1, E = 0;

        private void Button_check2_Click(object sender, EventArgs e)
        {
            try
            {
                double x = Convert.ToDouble(Convert.ToUInt32(textBox_in_check.Text, 16));
                double y = E;
                y += A * Math.Pow(x, 4);
                y += B * Math.Pow(x, 3);
                y += C * Math.Pow(x, 2);
                y += D * x;
                textBox_ex_check.Text = y.ToString();
            }
            catch (Exception)
            {

                throw;
            }
        }

        private void Button_cali2_Click(object sender, EventArgs e)
        {
            TextBox[] xBoxes = new TextBox[] { textBox_in1, textBox_in2, textBox_in3, textBox_in4, textBox_in5 };
            TextBox[] yBoxes = new TextBox[] { textBox_ex1, textBox_ex2, textBox_ex3, textBox_ex4, textBox_ex5 };
            GaussCancellation gauss = new GaussCancellation(yBoxes.Length);

            try
            {
                for (int i = 0; i < xBoxes.Length; i++)
                {
                    double x = Convert.ToDouble(Convert.ToUInt32(xBoxes[i].Text, 16));
                    for (int j = 0; j < xBoxes.Length; j++)
                    {
                        gauss.arr[i][j] = Math.Pow(x, 4 - j);
                    }
                    gauss.result[i] = Convert.ToDouble(yBoxes[i].Text);
                }

                gauss.Gauss();
                A = gauss.result[0];
                B = gauss.result[1];
                C = gauss.result[2];
                D = gauss.result[3];
                E = gauss.result[4];

                textBox_A.Text = A.ToString();
                textBox_B.Text = B.ToString();
                textBox_C.Text = C.ToString();
                textBox_D.Text = D.ToString();
                textBox_E.Text = E.ToString();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        public Form1()
        {
            InitializeComponent();
        }

        private void Button_check_Click(object sender, EventArgs e)
        {
            try
            {
                double x = Convert.ToDouble(Convert.ToUInt32(textBox_X3.Text, 16));
                double y = x * slope + offset;

                textBox_Y3.Text = y.ToString();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void Button_cali_Click(object sender, EventArgs e)
        {
            GaussCancellation gauss = new GaussCancellation(2);

            try
            {
                gauss.arr[0][0] = Convert.ToDouble(Convert.ToUInt32(textBox_X1.Text, 16));
                gauss.arr[1][0] = Convert.ToDouble(Convert.ToUInt32(textBox_X2.Text, 16));
                gauss.arr[0][1] = 1;
                gauss.arr[1][1] = 1;
                gauss.result[0] = Convert.ToDouble(textBox_Y1.Text);
                gauss.result[1] = Convert.ToDouble(textBox_Y2.Text);

                gauss.Gauss();

                slope = gauss.result[0];
                offset = gauss.result[1];

                textBox_slope.Text = slope.ToString();
                textBox_offset.Text = offset.ToString();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
