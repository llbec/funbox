namespace Convertor
{
    partial class CalibrationControl
    {
        /// <summary> 
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region 组件设计器生成的代码

        /// <summary> 
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.textBox_order = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.groupBox_body = new System.Windows.Forms.GroupBox();
            this.SuspendLayout();
            // 
            // textBox_order
            // 
            this.textBox_order.Location = new System.Drawing.Point(41, 31);
            this.textBox_order.Name = "textBox_order";
            this.textBox_order.Size = new System.Drawing.Size(46, 21);
            this.textBox_order.TabIndex = 0;
            this.textBox_order.Text = "4";
            this.textBox_order.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(93, 36);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(53, 12);
            this.label1.TabIndex = 1;
            this.label1.Text = "阶多项式";
            // 
            // groupBox_body
            // 
            this.groupBox_body.Location = new System.Drawing.Point(41, 71);
            this.groupBox_body.Name = "groupBox_body";
            this.groupBox_body.Size = new System.Drawing.Size(859, 481);
            this.groupBox_body.TabIndex = 3;
            this.groupBox_body.TabStop = false;
            this.groupBox_body.Text = "Ax^4 + Bx^3 + Cx^2 + Dx + E";
            // 
            // CalibrationControl
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.groupBox_body);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.textBox_order);
            this.Name = "CalibrationControl";
            this.Size = new System.Drawing.Size(976, 680);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox textBox_order;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.GroupBox groupBox_body;
    }
}
