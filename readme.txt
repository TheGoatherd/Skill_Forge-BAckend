import java.io.*;import java.util.*;
public class Main{
    static class BIT{int n,t[];BIT(int n){this.n=n;t=new int[n+1];}void add(int i,int d){for(;i<=n;i+=i&-i)t[i]+=d;}int sum(int i){int s=0;for(;i>0;i-=i&-i)s+=t[i];return s;}}
    public static void main(String[]a)throws Exception{
        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));
        int n=Integer.parseInt(br.readLine().trim());
        int[] val=new int[n],s=new int[n];
        StringTokenizer st=new StringTokenizer(br.readLine());
        for(int i=0;i<n;i++)s[i]=val[i]=Integer.parseInt(st.nextToken());
        List<Integer>[] g=new ArrayList[n];for(int i=0;i<n;i++)g[i]=new ArrayList<>();
        for(int i=0;i<n-1;i++){st=new StringTokenizer(br.readLine());int u=Integer.parseInt(st.nextToken()),v=Integer.parseInt(st.nextToken());g[u].add(v);g[v].add(u);}
        Arrays.sort(s);int m=1;for(int i=1;i<n;i++)if(s[i]!=s[i-1])s[m++]=s[i];
        int[] comp=new int[n];for(int i=0;i<n;i++)comp[i]=1+Arrays.binarySearch(s,0,m,val[i]);
        BIT bit=new BIT(m);long ans=0;int[][] stk=new int[2*n][3];int top=0;stk[top++]=new int[]{0,-1,0};
        while(top>0){int[] e=stk[--top];int node=e[0],par=e[1],type=e[2];
            if(type==0){bit.add(comp[node],1);stk[top++]=new int[]{node,par,1};for(int nxt:g[node])if(nxt!=par){ans+=bit.sum(comp[nxt]-1);stk[top++]=new int[]{nxt,node,0};}}
            else bit.add(comp[node],-1);}
        System.out.println(ans);
    }
}
