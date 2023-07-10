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
        private double Order4A = 0, Order4B = 0, Order4C = 0, Order4D = 1, Order4E = 0;
        private double Order2A = 0, Order2B = 1, Order2C = 0;

        private void Button_2_check_Click(object sender, EventArgs e)
        {
            try
            {
                double x = Convert.ToDouble(Convert.ToUInt32(textBox_2_check_in.Text, 16));
                double y = Order2C;
                y += Order2A * Math.Pow(x, 2);
                y += Order2B * x;
                textBox_2_check_ex.Text = y.ToString();
            }
            catch (Exception)
            {

                throw;
            }
        }

        private void Button_2_cali_Click(object sender, EventArgs e)
        {
            TextBox[] xBoxes = new TextBox[] { textBox_2_in1, textBox_2_in2, textBox_2_in3 };
            TextBox[] yBoxes = new TextBox[] { textBox_2_ex1, textBox_2_ex2, textBox_2_ex3 };
            GaussCancellation gauss = new GaussCancellation(yBoxes.Length);

            try
            {
                int order = xBoxes.Length - 1;
                for (int i = 0; i < xBoxes.Length; i++)
                {
                    double x = Convert.ToDouble(Convert.ToUInt32(xBoxes[i].Text, 16));
                    for (int j = 0; j < xBoxes.Length; j++)
                    {
                        gauss.arr[i][j] = Math.Pow(x, order - j);
                    }
                    gauss.result[i] = Convert.ToDouble(yBoxes[i].Text);
                }

                gauss.Gauss();
                Order2A = gauss.result[0];
                Order2B = gauss.result[1];
                Order2C = gauss.result[2];

                textBox_2_A.Text = Order2A.ToString();
                textBox_2_B.Text = Order2B.ToString();
                textBox_2_C.Text = Order2C.ToString();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void Button_check2_Click(object sender, EventArgs e)
        {
            try
            {
                double x = Convert.ToDouble(Convert.ToUInt32(textBox_4_in_check.Text, 16));
                double y = Order4E;
                y += Order4A * Math.Pow(x, 4);
                y += Order4B * Math.Pow(x, 3);
                y += Order4C * Math.Pow(x, 2);
                y += Order4D * x;
                textBox_4_ex_check.Text = y.ToString();
            }
            catch (Exception)
            {

                throw;
            }
        }

        private void Button_cali2_Click(object sender, EventArgs e)
        {
            TextBox[] xBoxes = new TextBox[] { textBox_4_in1, textBox_4_in2, textBox_4_in3, textBox_4_in4, textBox_4_in5 };
            TextBox[] yBoxes = new TextBox[] { textBox_4_ex1, textBox_4_ex2, textBox_4_ex3, textBox_4_ex4, textBox_4_ex5 };
            GaussCancellation gauss = new GaussCancellation(yBoxes.Length);

            try
            {
                int order = xBoxes.Length - 1;
                for (int i = 0; i < xBoxes.Length; i++)
                {
                    double x = Convert.ToDouble(Convert.ToUInt32(xBoxes[i].Text, 16));
                    for (int j = 0; j < xBoxes.Length; j++)
                    {
                        gauss.arr[i][j] = Math.Pow(x, order - j);
                    }
                    gauss.result[i] = Convert.ToDouble(yBoxes[i].Text);
                }

                gauss.Gauss();
                Order4A = gauss.result[0];
                Order4B = gauss.result[1];
                Order4C = gauss.result[2];
                Order4D = gauss.result[3];
                Order4E = gauss.result[4];

                textBox_4_A.Text = Order4A.ToString();
                textBox_4_B.Text = Order4B.ToString();
                textBox_4_C.Text = Order4C.ToString();
                textBox_4_D.Text = Order4D.ToString();
                textBox_4_E.Text = Order4E.ToString();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        public Form1()
        {
            InitializeComponent();
            
            TabPage caliPage = new TabPage() { Text = "Calibration" };
            tabControl_main.Controls.Add(caliPage);
            caliPage.Controls.Add(new CalibrationControl());
        }

        private void Button_check_Click(object sender, EventArgs e)
        {
            try
            {
                double x = Convert.ToDouble(Convert.ToUInt32(textBox_1_in_check.Text, 16));
                double y = x * slope + offset;

                textBox_1_ex_check.Text = y.ToString();
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
                gauss.arr[0][0] = Convert.ToDouble(Convert.ToUInt32(textBox_1_in1.Text, 16));
                gauss.arr[1][0] = Convert.ToDouble(Convert.ToUInt32(textBox_1_in2.Text, 16));
                gauss.arr[0][1] = 1;
                gauss.arr[1][1] = 1;
                gauss.result[0] = Convert.ToDouble(textBox_1_ex1.Text);
                gauss.result[1] = Convert.ToDouble(textBox_1_ex2.Text);

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
