#include <stdio.h>
void main()
{	
	FILE *fp;
	char filename[40]  ;
	int i,j ;
    float da[6][5] = {0} ;
    printf(" 输入文件名: ");
    gets(filename);
    fp=fopen(filename,"r");     // fp指针指向文件头部
    for(i = 0 ;i < 6 ; i++)
        for(j = 0 ;j < 5 ; j++)
        {
			fscanf(fp,"%f",&da[i][j]);
			fseek(fp, 5L, SEEK_CUR);   /*fp指针从当前位置向后移动*/
		}
           
    for(i = 0 ;i < 6 ; i++)
        printf("%f\t%f\t%f\t%f\t%f\t\n",da[i][0],
         da[i][1],da[i][2],da[i][3],da[i][4]);
}
