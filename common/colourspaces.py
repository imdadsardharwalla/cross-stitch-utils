import numpy as np

RGB_max = 255.0

# ITU-R BT.2020 conversion
Kb = 0.0593
Kr = 0.2627
Kg = 1 - Kr - Kb

def RGB_to_YPbPr (rgb, y_boost):
    [R, G, B] = rgb

    R /= RGB_max
    G /= RGB_max
    B /= RGB_max

    Y  = Kr * R + Kg * G + Kb * B
    Pb = 0.5 * (B - Y) / (1 - Kb)
    Pr = 0.5 * (R - Y) / (1 - Kr)

    Y *= y_boost

    return np.array ([Y, Pb, Pr])

def YPbPr_to_RGB (ypbpr, y_boost):
    [Y, Pb, Pr] = ypbpr

    Y /= y_boost

    B = Y + 2.0 * Pb * (1 - Kb)
    R = Y + 2.0 * Pr * (1 - Kr)
    G = (Y - Kr * R - Kb * B) / Kg

    R *= RGB_max
    G *= RGB_max
    B *= RGB_max

    return np.array ([R, G, B])

def RGB_to_HSL (rgb):
    [R, G, B] = rgb

    R /= RGB_max
    G /= RGB_max
    B /= RGB_max

    m = min ([R, G, B])
    M = max ([R, G, B])
    C = M - m

    L = 0.5 * (m + M)

    if C <= 0:
        S = 0
        H = 0
    else:
        if L < 0.5:
            S = C / (M + m)
        else:
            S = C / (2.0 - M - m)

        if R >= G and R >= B:
            H = (G - B) / C
        elif G >= R and G >= B:
            H = 2.0 + (B - R) / C
        else:
            H = 4.0 + (R - G) / C

        H *= 60.0
        H = H % 360

    return np.array ([H, S, L])

def HSL_to_RGB (hsl):
    [H, S, L] = hsl

    if S == 0:
        assert H == 0
        R = L
        G = L
        B = L
    else:
        tmp_1 = None
        if L < 0.5:
            tmp_1 = L * (1.0 + S)
        else:
            tmp_1 = L + S - L * S

        tmp_2 = 2 * L - tmp_1

        H /= 360.0

        tmp_R = (H + 1.0 / 3.0) % 1
        tmp_G = (H            ) % 1
        tmp_B = (H - 1.0 / 3.0) % 1

        if tmp_R < 1.0 / 6.0:
            R = tmp_2 + (tmp_1 - tmp_2) * 6.0 * tmp_R
        elif tmp_R < 1.0 / 2.0:
            R = tmp_1
        elif tmp_R < 2.0 / 3.0:
            R = tmp_2 + (tmp_1 - tmp_2) * (2.0 / 3.0 - tmp_R) * 6.0
        else:
            R = tmp_2

        if tmp_G < 1.0 / 6.0:
            G = tmp_2 + (tmp_1 - tmp_2) * 6.0 * tmp_G
        elif tmp_G < 1.0 / 2.0:
            G = tmp_1
        elif tmp_G < 2.0 / 3.0:
            G = tmp_2 + (tmp_1 - tmp_2) * (2.0 / 3.0 - tmp_G) * 6.0
        else:
            G = tmp_2

        if tmp_B < 1.0 / 6.0:
            B = tmp_2 + (tmp_1 - tmp_2) * 6.0 * tmp_B
        elif tmp_B < 1.0 / 2.0:
            B = tmp_1
        elif tmp_B < 2.0 / 3.0:
            B = tmp_2 + (tmp_1 - tmp_2) * (2.0 / 3.0 - tmp_B) * 6.0
        else:
            B = tmp_2

    R *= RGB_max
    G *= RGB_max
    B *= RGB_max

    return np.array ([R, G, B])

def HSL_sort (hsl):
    [R, G, B, H, S, L] = hsl
    return 1000.0 * H + 500.0 * L + S
