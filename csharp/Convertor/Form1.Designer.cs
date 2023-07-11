namespace Convertor
{
    partial class Form1
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

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.tabControl_main = new System.Windows.Forms.TabControl();
            this.caliPage = new System.Windows.Forms.TabPage();
            this.tabControl_main.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControl_main
            // 
            this.tabControl_main.Controls.Add(this.caliPage);
            this.tabControl_main.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabControl_main.Location = new System.Drawing.Point(0, 0);
            this.tabControl_main.Name = "tabControl_main";
            this.tabControl_main.SelectedIndex = 0;
            this.tabControl_main.Size = new System.Drawing.Size(1185, 714);
            this.tabControl_main.TabIndex = 3;
            // 
            // tabPage1
            // 
            this.caliPage.Location = new System.Drawing.Point(4, 22);
            this.caliPage.Name = "tabPage1";
            this.caliPage.Padding = new System.Windows.Forms.Padding(3);
            this.caliPage.Size = new System.Drawing.Size(1177, 688);
            this.caliPage.TabIndex = 0;
            this.caliPage.Text = "tabPage1";
            this.caliPage.UseVisualStyleBackColor = true;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1185, 714);
            this.Controls.Add(this.tabControl_main);
            this.Name = "Form1";
            this.Text = "Form1";
            this.tabControl_main.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.TabControl tabControl_main;
        private System.Windows.Forms.TabPage caliPage;
    }
}

