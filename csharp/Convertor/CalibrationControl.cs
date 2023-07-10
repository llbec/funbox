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
        int order;
        ComboBox hexaComboBox;
        TextBox[][] sampleBoxes;
        TextBox[] checkBoxes;
        Label[] caliLabels;

        public CalibrationControl()
        {
            InitializeComponent();
            order = int.Parse(textBox_order.Text);

            BodyView();
        }

        private void BodyView()
        {
            int num = order + 1;
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
            groupBox_body.Controls.Add(new Button()
            {
                Text = "验证",
                Size = new Size(47, 20),
                Location = new Point(x, y),
            });

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
            x = 100 + 100 + 30 + 100;
            y = 40 + 30;
        }
    }
}
