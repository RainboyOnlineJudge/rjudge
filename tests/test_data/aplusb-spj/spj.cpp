/* 
 * 接收三个参数
 * input  输入文件
 * output 输出文件
 * ans    标准输出文件
 * */
#include <cstdio>
#include <cstdlib>



typedef long long ll;

int main(int argc,char *argv[]){
    FILE* fin  = fopen(argv[1],"r");
    FILE* fout = fopen(argv[2],"r");
    FILE* fans = fopen(argv[3],"r");

    ll out;
    ll ans;

    fscanf(fout,"%lld",&out);
    fscanf(fans,"%lld",&ans);

    bool flag  =false;
    /* 如果两者相差不到10 就对 */
    if( abs(out -ans) <= 10){
        flag =true;
    }

    fclose(fin);
    fclose(fout);
    fclose(fans);
    return flag?0:1;
}
