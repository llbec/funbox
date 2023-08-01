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
    public partial class CalibrationControl : UserControl
    {
        int order, num;
        ComboBox hexaComboBox;
        ComboBox precisionComboBox;
        TextBox[][] sampleBoxes;
        TextBox[] checkBoxes;
        Label[] caliLabels;
        double[] vals;

        private const string DOUBLE_FORMAT = "f10";

        public CalibrationControl()
        {
            InitializeComponent();

            BodyView();
        }

        private void BodyView()
        {
            order = int.Parse(textBox_order.Text);
            vals = new double[order + 1];
            vals[vals.Length - 2] = 1;
            num = order + 1;

            int x = 107, y = 40;
            groupBox_body.Controls.Clear();

            groupBox_body.Controls.Add(new Label()
            {
                Text = "内部值",
                Location = new Point(x, y),
                AutoSize = false,
                Size = new Size(41, 20),
                TextAlign = ContentAlignment.MiddleCenter
            });
            x += 45;

            hexaComboBox = new ComboBox()
            {
                Location = new Point(x, y),
                Size = new Size(41, 20),
                DropDownStyle = ComboBoxStyle.DropDownList,
            };
            hexaComboBox.Items.Add("HEX");
            hexaComboBox.Items.Add("DEC");
            hexaComboBox.SelectedIndex = 0;
            groupBox_body.Controls.Add(hexaComboBox);
            x += 41 + 7 + 30 + 17;

            groupBox_body.Controls.Add(new Label()
            {
                Text = "测试仪器值",
                Location = new Point(x, y),
                AutoSize = false,
                Size = new Size(65, 20),
                TextAlign = ContentAlignment.MiddleCenter
            });

            // 采样Label加2个TextBox
            sampleBoxes = new TextBox[num][];
            for (int i = 0; i < num; i++)
            {
                y += 30;
                x = 35;
                groupBox_body.Controls.Add(new Label()
                {
                    Text = string.Format("采样{0}", i),
                    Location = new Point(x, y),
                    AutoSize = false,
                    Size = new Size(35, 20),
                    TextAlign = ContentAlignment.MiddleRight
                });

                x = 100;
                sampleBoxes[i] = new TextBox[2];
                for (int j = 0; j < 2; j++)
                {
                    sampleBoxes[i][j] = new TextBox()
                    {
                        Size = new Size(100, 20),
                        Location = new Point(x, y),
                        TextAlign = HorizontalAlignment.Center,
                    };
                    groupBox_body.Controls.Add(sampleBoxes[i][j]);
                    x += 100 + 30;
                }
            }

            // 验证 1 Button & 2 TextBox
            checkBoxes = new TextBox[2];
            y += 20 + 40;
            x = 25;
            Button verifyBTN = new Button()
            {
                Text = "验证",
                Size = new Size(47, 20),
                Location = new Point(x, y),
            };
            verifyBTN.Click += Verify_ButtonClick;
            groupBox_body.Controls.Add(verifyBTN);

            x = 100;
            for (int i = 0; i < 2; i++)
            {
                checkBoxes[i] = new TextBox()
                {
                    Size = new Size(100, 20),
                    Location = new Point(x, y),
                    TextAlign = HorizontalAlignment.Center,
                    ReadOnly = i == 1,
                };
                groupBox_body.Controls.Add(checkBoxes[i]);
                x += 100 + 30;
            }

            // 校准 1个 Button，竖排Label， 1个comboBox
            caliLabels = new Label[num];
            x = 100 + 100 + 30 + 100 + 60;
            y = 40;
            Button btn = new Button()
            {
                Location = new Point(x + 2, y),
                Size = new Size(47, 20),
                Text = "校准",
            };
            btn.Click += Cali_ButtonClick;
            groupBox_body.Controls.Add(btn);

            precisionComboBox = new ComboBox()
            {
                Location = new Point(x + 54, y),
                Size = new Size(41, 20),
                DropDownStyle = ComboBoxStyle.DropDownList,
            };
            precisionComboBox.Items.Add("32");
            precisionComboBox.Items.Add("16");
            precisionComboBox.SelectedIndex = 0;
            groupBox_body.Controls.Add(precisionComboBox);

            for (int i = 0; i < num; i++)
            {
                y += 30;
                caliLabels[i] = new Label()
                {
                    AutoSize = false,
                    Location = new Point(x, y),
                    Size = new Size(100, 20),
                    TextAlign = ContentAlignment.MiddleCenter,
                    BackColor = Color.Gainsboro,
                    Text = vals[i].ToString(),
                };
                groupBox_body.Controls.Add(caliLabels[i]);
                groupBox_body.Controls.Add(new Label()
                {
                    Location = new Point(x + 102, y + 4),
                    Text = string.Format("x^{0}", order - i),
                });
            }
        }

        private double Precision(double src)
        {
            double ret = src;
            if (precisionComboBox.SelectedIndex == 1)
            {
                int t = (int)(src * 256);
                ret = t / 256;
            }
            return ret;
        }

        private void TextBox_order_TextChanged(object sender, EventArgs e)
        {
            try
            {
                if (order == int.Parse(textBox_order.Text)) return;
                if (int.Parse(textBox_order.Text) < 1)
                {
                    textBox_order.Text = order.ToString();
                    return;
                }
                BodyView();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void Cali_ButtonClick(object sender, EventArgs e)
        {
            GaussCancellation gauss = new GaussCancellation(num);

            try
            {
                for (int i = 0; i < num; i++)
                {
                    double para = hexaComboBox.SelectedIndex == 0 ? Convert.ToDouble(Convert.ToInt32(sampleBoxes[i][0].Text, 16)) : double.Parse(sampleBoxes[i][0].Text);
                    for (int j = 0; j < num; j++)
                    {
                        gauss.arr[i][j] = Math.Pow(para, order - j);
                    }
                    gauss.result[i] = Convert.ToDouble(sampleBoxes[i][1].Text);
                }

                gauss.Gauss();
                for (int i = 0; i < num; i++)
                {
                    vals[i] = gauss.result[i];
                    caliLabels[i].Text = vals[i].ToString(DOUBLE_FORMAT);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void Verify_ButtonClick(object sender, EventArgs e)
        {
            try
            {
                double para = hexaComboBox.SelectedIndex == 0 ? Convert.ToDouble(Convert.ToInt32(checkBoxes[0].Text, 16)) : double.Parse(checkBoxes[0].Text);
                double result = 0;
                for (int i = 0; i < num; i++)
                {
                    result += i == order ? vals[i] : Math.Pow(para, order - i) * Precision(vals[i]);
                }
                checkBoxes[1].Text = result.ToString(DOUBLE_FORMAT);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
