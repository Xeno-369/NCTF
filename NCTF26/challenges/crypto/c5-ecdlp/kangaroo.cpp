#include <iostream>
#include <vector>
#include <unordered_map>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <omp.h>

using namespace std;
using u128 = __uint128_t;

u128 str_to_u128(const char* s) {
    u128 res = 0;
    while (*s) {
        if (*s >= '0' && *s <= '9') res = res * 10 + (*s - '0');
        s++;
    }
    return res;
}

const u128 P = str_to_u128("175452152274950681233185340816407921607");
const u128 A = str_to_u128("98454893137132264546748386023684856511");

inline u128 add_mod(u128 a, u128 b) {
    a += b;
    return (a >= P) ? (a - P) : a;
}

inline u128 sub_mod(u128 a, u128 b) {
    return (a >= b) ? (a - b) : (P - b + a);
}

inline u128 mul_mod(u128 a, u128 b) {
    u128 res = 0;
    a %= P;
    while (b > 0) {
        if (b & 1) res = add_mod(res, a);
        a = add_mod(a, a);
        b >>= 1;
    }
    return res;
}

u128 inv_mod(u128 a) {
    u128 t = 0, newt = 1;
    u128 r = P, newr = a % P;
    while (newr != 0) {
        u128 q = r / newr;
        u128 tmp_t = t; t = newt; newt = tmp_t - q * newt;
        u128 tmp_r = r; r = newr; newr = tmp_r - q * newr;
    }
    if (r > 1) return 0;
    if ((__int128_t)t < 0) t += P;
    return t % P;
}

struct Point {
    u128 x, y;
    bool inf;
};

Point point_add(const Point& P1, const Point& P2) {
    if (P1.inf) return P2;
    if (P2.inf) return P1;
    u128 num, den;
    if (P1.x == P2.x) {
        if (P1.y != P2.y || P1.y == 0) return {0, 0, true};
        u128 x2 = mul_mod(P1.x, P1.x);
        num = add_mod(add_mod(x2, x2), add_mod(x2, A));
        den = add_mod(P1.y, P1.y);
    } else {
        num = sub_mod(P2.y, P1.y);
        den = sub_mod(P2.x, P1.x);
    }
    u128 inv = inv_mod(den);
    if (inv == 0) return {0, 0, true};
    u128 lam = mul_mod(num, inv);
    u128 x3 = sub_mod(sub_mod(mul_mod(lam, lam), P1.x), P2.x);
    u128 y3 = sub_mod(mul_mod(lam, sub_mod(P1.x, x3)), P1.y);
    return {x3, y3, false};
}

Point point_mul(Point base, uint64_t k) {
    Point res = {0, 0, true};
    while (k > 0) {
        if (k & 1) res = point_add(res, base);
        base = point_add(base, base);
        k >>= 1;
    }
    return res;
}

int main() {
    Point G = {
        str_to_u128("14211931093213991535394460705985328640"),
        str_to_u128("68285343446490133732558751282171566849"),
        false
    };
    Point Q = {
        str_to_u128("33959484871420591504873648003783896046"),
        str_to_u128("145738767669641093961271706546716373511"),
        false
    };

    const int K = 32;
    uint64_t jumps[K];
    Point jump_pts[K];
    for (int i = 0; i < K; ++i) {
        jumps[i] = 1ULL << i;
        jump_pts[i] = point_mul(G, jumps[i]);
    }

    const uint64_t DP_MASK = (1ULL << 18) - 1;
    unordered_map<uint64_t, pair<uint64_t, bool>> table;
    atomic<bool> found(false);
    atomic<uint64_t> total_ops(0);
    uint64_t secret_x = 0;
    auto start_time = chrono::steady_clock::now();

    cout << "[*] Lancement sur " << omp_get_max_threads() << " threads..." << endl;

    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        bool is_tame = (tid % 2 == 0);
        uint64_t dist = is_tame ? ((1ULL << 62) + (uint64_t)tid * (1ULL << 38)) : ((uint64_t)tid * (1ULL << 38));
        Point cur = is_tame ? point_mul(G, dist) : point_add(Q, point_mul(G, dist));

        uint64_t local_ops = 0;
        while (!found.load(memory_order_relaxed)) {
            uint64_t x_low = (uint64_t)cur.x;
            int idx = x_low & (K - 1);
            cur = point_add(cur, jump_pts[idx]);
            dist += jumps[idx];
            local_ops++;

            if ((local_ops & 0xFFFFF) == 0) {
                uint64_t tot = total_ops.fetch_add(0x100000) + 0x100000;
                if (tid == 0) {
                    auto now = chrono::steady_clock::now();
                    double sec = chrono::duration<double>(now - start_time).count();
                    cout << "\r[*] Ops: " << (tot / 1000000) << "M | Vitesse: " << (uint64_t)(tot / sec / 1000) << " kOps/s | Table: " << table.size() << "   " << flush;
                }
            }

            if ((x_low & DP_MASK) == 0) {
                #pragma omp critical
                {
                    if (!found.load()) {
                        auto it = table.find(x_low);
                        if (it != table.end() && it->second.second != is_tame) {
                            uint64_t tame_d = is_tame ? dist : it->second.first;
                            uint64_t wild_d = is_tame ? it->second.first : dist;
                            if (tame_d >= wild_d) {
                                secret_x = tame_d - wild_d;
                                found.store(true);
                            }
                        } else {
                            table[x_low] = {dist, is_tame};
                        }
                    }
                }
            }
        }
    }

    cout << "\n[+] SECRET TROUVE : x = " << secret_x << endl;
    return 0;
}
