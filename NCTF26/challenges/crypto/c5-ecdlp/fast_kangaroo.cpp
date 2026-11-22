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

// Multiplication rapide 128x128 mod P (sans boucle bit-à-bit lente)
inline u128 add_mod(u128 a, u128 b) {
    a += b;
    return (a >= P) ? (a - P) : a;
}

inline u128 sub_mod(u128 a, u128 b) {
    return (a >= b) ? (a - b) : (P - b + a);
}

inline u128 mul_mod(u128 a, u128 b) {
    uint64_t a0 = (uint64_t)a, a1 = (uint64_t)(a >> 64);
    uint64_t b0 = (uint64_t)b, b1 = (uint64_t)(b >> 64);
    u128 p0 = (u128)a0 * b0;
    u128 p1 = (u128)a0 * b1 + (u128)a1 * b0 + (p0 >> 64);
    u128 p2 = (u128)a1 * b1 + (p1 >> 64);
    
    // Réduction rapide : 2^128 mod P = 2^128 - P
    const u128 R128 = ((u128)0 - P); 
    u128 lo = (p1 << 64) | (uint64_t)p0;
    
    // p2 * R128 + lo (avec p2 < 2^127 et R128 < 2^65)
    uint64_t hi0 = (uint64_t)p2, hi1 = (uint64_t)(p2 >> 64);
    uint64_t r0 = (uint64_t)R128, r1 = (uint64_t)(R128 >> 64);
    u128 m0 = (u128)hi0 * r0;
    u128 m1 = (u128)hi0 * r1 + (u128)hi1 * r0 + (m0 >> 64);
    u128 m2 = (u128)hi1 * r1 + (m1 >> 64);
    
    u128 res = lo % P;
    u128 mid = ((m1 << 64) | (uint64_t)m0) % P;
    res = add_mod(res, mid);
    // m2 < 2^65
    u128 top = (m2 * R128) % P;
    return add_mod(res, top);
}

u128 inv_mod(u128 a) {
    u128 t = 0, newt = 1;
    u128 r = P, newr = a % P;
    while (newr != 0) {
        u128 q = r / newr;
        u128 tmp_t = t; t = newt; newt = tmp_t - q * newt;
        u128 tmp_r = r; r = newr; newr = tmp_r - q * newr;
    }
    if ((__int128_t)t < 0) t += P;
    return t % P;
}

struct AffPoint { u128 x, y; bool inf; };
struct JacPoint { u128 X, Y, Z; };

// Addition mixte Jacobien + Affine (Z2 = 1) : 8 multiplications, 0 division
inline void add_mixed(JacPoint& R, const JacPoint& P1, const AffPoint& P2) {
    if (P1.Z == 0) { R = {P2.x, P2.y, 1}; return; }
    u128 Z1Z1 = mul_mod(P1.Z, P1.Z);
    u128 U2 = mul_mod(P2.x, Z1Z1);
    u128 S2 = mul_mod(P2.y, mul_mod(P1.Z, Z1Z1));
    u128 H = sub_mod(U2, P1.X);
    u128 HH = mul_mod(H, H);
    u128 I = add_mod(HH, HH); I = add_mod(I, I);
    u128 J = mul_mod(H, I);
    u128 r = sub_mod(S2, P1.Y); r = add_mod(r, r);
    u128 V = mul_mod(P1.X, I);
    
    u128 X3 = sub_mod(sub_mod(mul_mod(r, r), J), add_mod(V, V));
    u128 Y3 = sub_mod(mul_mod(r, sub_mod(V, X3)), add_mod(mul_mod(P1.Y, J), mul_mod(P1.Y, J)));
    u128 Z3 = sub_mod(sub_mod(mul_mod(add_mod(P1.Z, H), add_mod(P1.Z, H)), Z1Z1), HH);
    R = {X3, Y3, Z3};
}

AffPoint aff_add(const AffPoint& P1, const AffPoint& P2) {
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
    u128 lam = mul_mod(num, inv_mod(den));
    u128 x3 = sub_mod(sub_mod(mul_mod(lam, lam), P1.x), P2.x);
    u128 y3 = sub_mod(mul_mod(lam, sub_mod(P1.x, x3)), P1.y);
    return {x3, y3, false};
}

AffPoint aff_mul(AffPoint base, uint64_t k) {
    AffPoint res = {0, 0, true};
    while (k > 0) {
        if (k & 1) res = aff_add(res, base);
        base = aff_add(base, base);
        k >>= 1;
    }
    return res;
}

int main() {
    AffPoint G = {str_to_u128("14211931093213991535394460705985328640"), str_to_u128("68285343446490133732558751282171566849"), false};
    AffPoint Q = {str_to_u128("33959484871420591504873648003783896046"), str_to_u128("145738767669641093961271706546716373511"), false};

    const int K = 32;
    uint64_t jumps[K];
    AffPoint jump_pts[K];
    for (int i = 0; i < K; ++i) {
        jumps[i] = 1ULL << i;
        jump_pts[i] = aff_mul(G, jumps[i]);
    }

    // Batching de 128 kangourous par thread pour amortir l'inversion affine
    const int BATCH = 128;
    const uint64_t DP_MASK = (1ULL << 19) - 1;
    unordered_map<uint64_t, pair<uint64_t, bool>> table;
    atomic<bool> found(false);
    atomic<uint64_t> total_ops(0);
    uint64_t secret_x = 0;
    auto t0 = chrono::steady_clock::now();

    cout << "[*] Démarrage mode turbo sur " << omp_get_max_threads() << " threads..." << endl;

    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        vector<JacPoint> pts(BATCH);
        vector<uint64_t> dists(BATCH);
        vector<bool> tames(BATCH);

        for (int b = 0; b < BATCH; ++b) {
            int id = tid * BATCH + b;
            tames[b] = (id % 2 == 0);
            dists[b] = tames[b] ? ((1ULL << 62) + (uint64_t)id * (1ULL << 34)) : ((uint64_t)id * (1ULL << 34));
            AffPoint start = tames[b] ? aff_mul(G, dists[b]) : aff_add(Q, aff_mul(G, dists[b]));
            pts[b] = {start.x, start.y, 1};
        }

        uint64_t local_ops = 0;
        while (!found.load(memory_order_relaxed)) {
            for (int b = 0; b < BATCH; ++b) {
                uint64_t x_low = (uint64_t)pts[b].X;
                int idx = x_low & (K - 1);
                add_mixed(pts[b], pts[b], jump_pts[idx]);
                dists[b] += jumps[idx];
            }
            local_ops += BATCH;

            if ((local_ops & 0x3FFFFF) == 0) {
                uint64_t tot = total_ops.fetch_add(0x400000) + 0x400000;
                if (tid == 0) {
                    double sec = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
                    cout << "\r[*] Ops: " << (tot / 1000000) << "M | Vitesse: " << (uint64_t)(tot / sec / 1000000) << " MOps/s | Table: " << table.size() << "   " << flush;
                }
            }

            // Vérification DP périodique avec inversion de Montgomery groupée
            if ((local_ops & 0xFFF) == 0) {
                u128 prod[BATCH];
                prod[0] = pts[0].Z;
                for (int b = 1; b < BATCH; ++b) prod[b] = mul_mod(prod[b-1], pts[b].Z);
                u128 inv = inv_mod(prod[BATCH-1]);
                for (int b = BATCH - 1; b >= 0; --b) {
                    u128 z_inv = (b > 0) ? mul_mod(inv, prod[b-1]) : inv;
                    if (b > 0) inv = mul_mod(inv, pts[b].Z);
                    u128 z_inv2 = mul_mod(z_inv, z_inv);
                    u128 aff_x = mul_mod(pts[b].X, z_inv2);
                    u128 aff_y = mul_mod(pts[b].Y, mul_mod(z_inv2, z_inv));
                    pts[b] = {aff_x, aff_y, 1};

                    uint64_t xl = (uint64_t)aff_x;
                    if ((xl & DP_MASK) == 0) {
                        #pragma omp critical
                        {
                            if (!found.load()) {
                                auto it = table.find(xl);
                                if (it != table.end() && it->second.second != tames[b]) {
                                    uint64_t td = tames[b] ? dists[b] : it->second.first;
                                    uint64_t wd = tames[b] ? it->second.first : dists[b];
                                    if (td >= wd) {
                                        secret_x = td - wd;
                                        found.store(true);
                                    }
                                } else {
                                    table[xl] = {dists[b], tames[b]};
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    cout << "\n[+] SECRET TROUVE : x = " << secret_x << endl;
    return 0;
}
