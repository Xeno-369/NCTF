// Lee-Brickell ISD (p<=2) sur GF(2), multithread. Usage: isd <instance> <threads>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <stdatomic.h>
#include <unistd.h>
#include <time.h>
#define W 5
#define MAXM 300
#define MAXK 300
#define T 2
typedef uint64_t u64;
typedef struct { u64 w[W]; } row;
static int n, m, wt;
static row H[MAXM];
static atomic_int done;
static atomic_ullong iters;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
#define BIT(r, c) (((r).w[(c) >> 6] >> ((c) & 63)) & 1)
static inline u64 xs(u64 *s) { u64 x = *s; x ^= x << 13; x ^= x >> 7; x ^= x << 17; return *s = x; }
static void report(int t, const int *piv, const int *nz, int a, int b, const u64 *y) {
    pthread_mutex_lock(&mu);
    if (!atomic_exchange(&done, 1)) {
        printf("SOL t=%d:", t);
        for (int i = 0; i < m; i++) if ((y[i >> 6] >> (i & 63)) & 1) printf(" %d", piv[i]);
        if (a >= 0) printf(" %d", nz[a]);
        if (b >= 0) printf(" %d", nz[b]);
        printf("\n"); fflush(stdout);
    }
    pthread_mutex_unlock(&mu);
}
static void *worker(void *arg) {
    u64 seed; FILE *f = fopen("/dev/urandom", "rb"); fread(&seed, 8, 1, f); fclose(f); seed |= 1;
    (void)arg;
    static _Thread_local row A[MAXM];
    int perm[W * 64], piv[MAXM], nz[MAXK]; char isp[W * 64];
    static _Thread_local u64 V[MAXK][3];
    for (int i = 0; i < n; i++) perm[i] = i;
    while (!atomic_load(&done)) {
        memcpy(A, H, sizeof(row) * m);
        for (int i = n - 1; i > 0; i--) { int j = xs(&seed) % (i + 1), t = perm[i]; perm[i] = perm[j]; perm[j] = t; }
        memset(isp, 0, n);
        int r = 0;
        for (int idx = 0; idx < n && r < m; idx++) {
            int c = perm[idx], p = -1;
            for (int i = r; i < m; i++) if (BIT(A[i], c)) { p = i; break; }
            if (p < 0) continue;
            row tmp = A[p]; A[p] = A[r]; A[r] = tmp;
            for (int i = 0; i < m; i++) if (i != r && BIT(A[i], c)) for (int w = 0; w < W; w++) A[i].w[w] ^= A[r].w[w];
            piv[r++] = c; isp[c] = 1;
        }
        if (r < m) continue;
        int k = 0;
        for (int c = 0; c < n; c++) if (!isp[c]) nz[k++] = c;
        memset(V, 0, sizeof(u64) * 3 * k);
        u64 S[T][3] = {{0}};
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < k; j++) if (BIT(A[i], nz[j])) V[j][i >> 6] |= 1ULL << (i & 63);
            for (int t = 0; t < T; t++) if (BIT(A[i], n + t)) S[t][i >> 6] |= 1ULL << (i & 63);
        }
        for (int t = 0; t < T; t++) {
            u64 *s = S[t];
            if (__builtin_popcountll(s[0]) + __builtin_popcountll(s[1]) + __builtin_popcountll(s[2]) == wt) report(t, piv, nz, -1, -1, s);
            for (int a = 0; a < k; a++) {
                u64 x0 = s[0] ^ V[a][0], x1 = s[1] ^ V[a][1], x2 = s[2] ^ V[a][2];
                if (__builtin_popcountll(x0) + __builtin_popcountll(x1) + __builtin_popcountll(x2) == wt - 1) { u64 y[3] = {x0, x1, x2}; report(t, piv, nz, a, -1, y); }
                for (int b = a + 1; b < k; b++) {
                    u64 y0 = x0 ^ V[b][0], y1 = x1 ^ V[b][1], y2 = x2 ^ V[b][2];
                    if (__builtin_popcountll(y0) + __builtin_popcountll(y1) + __builtin_popcountll(y2) == wt - 2) { u64 y[3] = {y0, y1, y2}; report(t, piv, nz, a, b, y); }
                }
            }
        }
        atomic_fetch_add(&iters, 1);
    }
    return NULL;
}
int main(int c, char **v) {
    if (c < 3) return 2;
    FILE *f = fopen(v[1], "r"); int nt = atoi(v[2]);
    if (!f || fscanf(f, "%d %d %d", &n, &m, &wt) != 3 || n + T > W * 64 || m > 192 || n - m > MAXK) return 3;
    for (int i = 0; i < m; i++) for (int w = 0; w < W; w++) if (fscanf(f, "%lx", &H[i].w[w]) != 1) return 4;
    fclose(f);
    pthread_t th[64];
    for (int i = 0; i < nt; i++) pthread_create(&th[i], NULL, worker, NULL);
    time_t t0 = time(NULL), last = t0;
    while (!atomic_load(&done)) {
        usleep(200000);
        time_t now = time(NULL);
        if (now - last >= 30) { last = now; fprintf(stderr, "%lds iters=%llu\n", (long)(now - t0), (unsigned long long)atomic_load(&iters)); }
    }
    for (int i = 0; i < nt; i++) pthread_join(th[i], NULL);
    fprintf(stderr, "fin %lds iters=%llu\n", (long)(time(NULL) - t0), (unsigned long long)atomic_load(&iters));
    return 0;
}
