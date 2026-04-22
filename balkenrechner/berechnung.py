"""
Balkenrechner - Berechnungsmodul
Einfeldträger mit Einzel- und Streckenlasten
"""
import numpy as np


def berechne_einfeldtraeger(L, lasten, streckenlast_q, EI=None, n=500):
    """
    Berechnet Auflagerkräfte, Querkraft- und Momentenlinie.

    L              : Balkenlänge [m]
    lasten         : Liste von (F [kN], a [m]) – Einzellasten
    streckenlast_q : Gleichmäßige Streckenlast [kN/m], 0 = keine
    EI             : Biegesteifigkeit [kNm²], None = keine Durchbiegung
    n              : Anzahl Stützstellen
    """
    x = np.linspace(0, L, n)

    # --- Auflagerkräfte (statisch bestimmt, A links, B rechts) ---
    # Momentengleichgewicht um A:  B * L = Summe(F_i * a_i) + q*L*L/2
    M_um_A = sum(F * a for F, a in lasten) + streckenlast_q * L * L / 2.0
    B = M_um_A / L
    A = sum(F for F, _ in lasten) + streckenlast_q * L - B

    # --- Querkraft Q(x) ---
    Q = np.zeros(n)
    for i, xi in enumerate(x):
        q_xi = A
        for F, a in lasten:
            if xi > a:
                q_xi -= F
        q_xi -= streckenlast_q * xi
        Q[i] = q_xi

    # --- Biegemoment M(x) ---
    M = np.zeros(n)
    for i, xi in enumerate(x):
        m_xi = A * xi
        for F, a in lasten:
            if xi > a:
                m_xi -= F * (xi - a)
        m_xi -= streckenlast_q * xi ** 2 / 2.0
        M[i] = m_xi

    ergebnisse = {
        "A": round(A, 4),
        "B": round(B, 4),
        "Q_max": round(float(np.max(np.abs(Q))), 4),
        "M_max": round(float(np.max(M)), 4),
        "M_max_pos": round(float(x[np.argmax(M)]), 4),
        "x": x.tolist(),
        "Q": Q.tolist(),
        "M": M.tolist(),
    }

    # --- Durchbiegung w(x) via numerische Integration (EI gegeben) ---
    if EI and EI > 0:
        dx = L / (n - 1)
        # EI * y'' = M  (y positive upward, positive M = sagging)
        # Doppelintegration mit Trapezregel, Startneigung unbekannt (C1)
        # S1(x) = integral_0^x M/EI dt  (ohne Integrationskonstante)
        S1 = np.zeros(n)
        for i in range(1, n):
            S1[i] = S1[i - 1] + 0.5 * (M[i - 1] + M[i]) / EI * dx
        # S2(x) = integral_0^x S1 dt
        S2 = np.zeros(n)
        for i in range(1, n):
            S2[i] = S2[i - 1] + 0.5 * (S1[i - 1] + S1[i]) * dx
        # Randbedingungen y(0)=0, y(L)=0  →  C1 = -S2(L)/L
        C1 = -S2[-1] / L
        y = C1 * x + S2                        # positive = aufwärts
        w = -y                                 # positive = abwärts (physikalisch)
        ergebnisse["w"] = w.tolist()
        ergebnisse["w_max"] = round(float(np.max(w)) * 1000, 4)        # mm, positiv = nach unten
        ergebnisse["w_max_pos"] = round(float(x[np.argmax(w)]), 4)

    return ergebnisse
