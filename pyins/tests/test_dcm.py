from numpy.testing import assert_allclose, run_module_suite
import numpy as np
from pyins import dcm


def test_from_basic():
    A1 = dcm.from_basic(1, 30)
    A1_true = np.array([
        [1, 0, 0],
        [0, 0.5 * 3**0.5, -0.5],
        [0, 0.5, 0.5 * 3**0.5]
    ])
    assert_allclose(A1, A1_true, rtol=1e-10)

    A2 = dcm.from_basic(2, 30)
    A2_true = np.array([
        [0.5 * 3 ** 0.5, 0, 0.5],
        [0, 1, 0],
        [-0.5, 0, 0.5 * 3**0.5]
    ])
    assert_allclose(A2, A2_true, rtol=1e-10)

    A3 = dcm.from_basic(3, 30)
    A3_true = np.array([
        [0.5 * 3**0.5, -0.5, 0],
        [0.5, 0.5 * 3**0.5, 0],
        [0, 0, 1]
    ])
    assert_allclose(A3, A3_true, rtol=1e-10)

    A4 = dcm.from_basic(3, [30, 60])
    A4_true = np.array([
        [[0.5 * 3**0.5, -0.5, 0],
         [0.5, 0.5 * 3**0.5, 0],
         [0, 0, 1]],
        [[0.5, -0.5 * 3**0.5, 0],
         [0.5 * 3**0.5, 0.5, 0],
         [0, 0, 1]]
    ])
    assert_allclose(A4, A4_true, rtol=1e-10)


def test_from_rv():
    rv1 = np.array([1, 0, 0]) * np.pi / 3
    A1 = dcm.from_rv(rv1)
    A1_true = np.array([[1, 0, 0],
                       [0, 0.5, -0.5 * np.sqrt(3)],
                       [0, 0.5 * np.sqrt(3), 0.5]])
    assert_allclose(A1, A1_true, rtol=1e-10)

    rv2 = np.array([1, 1, 1]) * 1e-10
    A2 = dcm.from_rv(rv2)
    A2_true = np.array([[1, -1e-10, 1e-10],
                        [1e-10, 1, -1e-10],
                        [-1e-10, 1e-10, 1]])
    assert_allclose(A2, A2_true, rtol=1e-10)

    n = np.array([-0.5, 1/np.sqrt(2), 0.5])
    theta = np.pi / 6
    rv3 = n * theta
    s = np.sin(theta)
    c = np.cos(theta)

    A3 = dcm.from_rv(rv3)
    A3_true = np.array([
        [(1-c)*n[0]*n[0] + c, (1-c)*n[0]*n[1] - n[2]*s,
         (1-c)*n[0]*n[2] + s*n[1]],
        [(1-c)*n[1]*n[0] + s*n[2], (1-c)*n[1]*n[1] + c,
         (1-c)*n[1]*n[2] - s*n[0]],
        [(1-c)*n[2]*n[0] - s*n[1], (1-c)*n[2]*n[1] + s*n[0],
         (1-c)*n[2]*n[2] + c]
    ])
    assert_allclose(A3, A3_true, rtol=1e-10)

    rv = np.empty((30, 3))
    rv[:10] = rv1
    rv[10:20] = rv2
    rv[20:] = rv3
    A_true = np.empty((30, 3, 3))
    A_true[:10] = A1_true
    A_true[10:20] = A2_true
    A_true[20:] = A3_true
    A = dcm.from_rv(rv)
    assert_allclose(A, A_true, rtol=1e-8)

    rv = rv[::4]
    A_true = A_true[::4]
    A = dcm.from_rv(rv)
    assert_allclose(A, A_true, rtol=1e-10)


def test_to_rv():
    A1 = np.identity(3)
    rv1 = dcm.to_rv(A1)
    assert_allclose(rv1, 0, atol=1e-10)

    rv2 = 1e-10 * np.ones(3)
    A2 = np.array([
        [1, -rv2[2], rv2[1]],
        [rv2[2], 1, -rv2[0]],
        [-rv2[1], rv2[0], 1]
    ])
    assert_allclose(dcm.to_rv(A2), rv2, rtol=1e-10)

    A3 = np.array([
        [1/2**0.5, 1/2**0.5, 0],
        [-1/2**0.5, 1/2**0.5, 0],
        [0, 0, 1]
    ])
    rv3 = np.array([0, 0, -np.pi / 4])
    assert_allclose(dcm.to_rv(A3), rv3, rtol=1e-10)

    A = np.empty((30, 3, 3))
    A[:10] = A1
    A[10:20] = A2
    A[20:30] = A3
    rv = np.empty((30, 3))
    rv[:10] = rv1
    rv[10:20] = rv2
    rv[20:] = rv3
    assert_allclose(dcm.to_rv(A), rv, rtol=1e-10)

    A = A[::4]
    rv = rv[::4]
    assert_allclose(dcm.to_rv(A), rv, rtol=1e-10)


def test_dcm_rv_conversion():
    # Test conversions on random inputs.
    rng = np.random.RandomState(0)

    axis = rng.randn(20, 3)
    axis /= np.linalg.norm(axis, axis=1)[:, np.newaxis]
    angle = rng.uniform(-np.pi, np.pi, size=axis.shape[0])
    rv = axis * angle[:, np.newaxis]
    rv[::5] *= 1e-8

    A = dcm.from_rv(rv)
    rv_from_A = dcm.to_rv(A)
    assert_allclose(rv, rv_from_A, rtol=1e-10)

    rv = rv[:5]
    A = A[:5]
    rv_from_A = dcm.to_rv(A)
    assert_allclose(rv, rv_from_A, rtol=1e-10)


def test_dcm_quat_conversion():
    np.random.seed(0)
    h = np.random.uniform(0, 360, 20)
    p = np.random.uniform(-90, 90, 20)
    r = np.random.uniform(-180, 180, 20)

    As = dcm.from_hpr(h, p, r)
    for A in As:
        q = dcm.to_quat(A)
        Ac = dcm.from_quat(q)
        assert_allclose(Ac, A, rtol=1e-14, atol=1e-16)

    q = dcm.to_quat(As)
    Asc = dcm.from_quat(q)
    assert_allclose(Asc, As, rtol=1e-14, atol=1e-16)


def test_dcm_mrp_conversion():
    np.random.seed(1)
    h = np.random.uniform(0, 360, 100)
    p = np.random.uniform(-90, 90, 100)
    r = np.random.uniform(-180, 180, 100)

    As = dcm.from_hpr(h, p, r)
    for A in As:
        grp = dcm.to_mrp(A)
        Ac = dcm.from_mrp(grp)
        assert_allclose(Ac, A, rtol=1e-14, atol=1e-15)

    grp = dcm.to_mrp(As)
    Asc = dcm.from_mrp(grp)
    assert_allclose(Asc, As, rtol=1e-14, atol=1e-15)


def test_dcm_gibbs_conversion():
    np.random.seed(1)
    h = np.random.uniform(0, 360, 100)
    p = np.random.uniform(-90, 90, 100)
    r = np.random.uniform(-180, 180, 100)

    As = dcm.from_hpr(h, p, r)
    for A in As:
        grp = dcm.to_gibbs(A)
        Ac = dcm.from_gibbs(grp)
        assert_allclose(Ac, A, rtol=1e-14, atol=1e-15)

    grp = dcm.to_gibbs(As)
    Asc = dcm.from_gibbs(grp)
    assert_allclose(Asc, As, rtol=1e-14, atol=1e-15)


def test_from_hpr():
    hpr1 = [30, 0, 0]
    A_true1 = np.array([[np.sqrt(3)/2, 0.5, 0],
                        [-0.5, np.sqrt(3)/2, 0],
                        [0, 0, 1]])
    assert_allclose(dcm.from_hpr(*hpr1), A_true1, rtol=1e-10)

    hpr2 = np.rad2deg([1e-10, 3e-10, -1e-10])
    A_true2 = np.array([[1, 1e-10, -1e-10],
                        [-1e-10, 1, -3e-10],
                        [1e-10, 3e-10, 1]])
    assert_allclose(dcm.from_hpr(*hpr2), A_true2, rtol=1e-8)

    hpr3 = [45, -30, 60]
    A_true3 = np.array([
        [-np.sqrt(6)/8 + np.sqrt(2)/4, np.sqrt(6)/4,
         np.sqrt(2)/8 + np.sqrt(6)/4],
        [-np.sqrt(2)/4 - np.sqrt(6)/8, np.sqrt(6)/4,
         -np.sqrt(6)/4 + np.sqrt(2)/8],
        [-0.75, -0.5, np.sqrt(3)/4]
    ])
    assert_allclose(dcm.from_hpr(*hpr3), A_true3, rtol=1e-8)

    hpr = np.vstack((hpr1, hpr2, hpr3)).T
    A = np.array((A_true1, A_true2, A_true3))
    assert_allclose(dcm.from_hpr(*hpr), A, rtol=1e-8)


def test_to_hpr():
    A1 = np.identity(3)
    hpr1 = np.zeros(3)
    assert_allclose(dcm.to_hpr(A1), hpr1, atol=1e-10)

    A2 = np.array([[1, 1e-10, -2e-10],
                   [-1e-10, 1, 3e-10],
                   [2e-10, -3e-10, 1]])
    hpr2 = np.rad2deg([1e-10, -3e-10, -2e-10])
    assert_allclose(dcm.to_hpr(A2), hpr2, atol=1e-10)

    A3 = np.array([
        [1/np.sqrt(2), 0, 1/np.sqrt(2)],
        [0, 1, 0],
        [-1/np.sqrt(2), 0, 1/np.sqrt(2)]
    ])
    hpr3 = np.array([0, 0, 45])
    assert_allclose(dcm.to_hpr(A3), hpr3, rtol=1e-10)

    A4 = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]])
    hpr4 = np.array([180, -90, 0])
    assert_allclose(dcm.to_hpr(A4), hpr4, rtol=1e-10)

    A = np.empty((20, 3, 3))
    A[:5] = A1
    A[5:10] = A2
    A[10:15] = A3
    A[15:] = A4
    hpr = np.empty((20, 3))
    hpr[:5] = hpr1
    hpr[5:10] = hpr2
    hpr[10:15] = hpr3
    hpr[15:20] = hpr4

    ret = dcm.to_hpr(A)
    for i in range(3):
        assert_allclose(ret[i], hpr[:, i], rtol=1e-10)


def test_dcm_hpr_conversion():
    rng = np.random.RandomState(0)

    h = rng.uniform(0, 360, 20)
    p = rng.uniform(-90, 90, 20)
    r = rng.uniform(-180, 180, 20)

    A = dcm.from_hpr(h, p, r)
    h_r, p_r, r_r = dcm.to_hpr(A)

    assert_allclose(h, h_r, rtol=1e-10)
    assert_allclose(p, p_r, rtol=1e-10)
    assert_allclose(r, r_r, rtol=1e-10)


def test_from_llw():
    llw1 = np.array([90, -90, 0])
    A1 = np.identity(3)
    assert_allclose(dcm.from_llw(*llw1), A1, rtol=1e-10, atol=1e-10)
    assert_allclose(dcm.from_llw(*llw1[:2]), A1, rtol=1e-10, atol=1e-10)

    llw2 = np.array([90, -90, np.rad2deg(1e-9)])
    A2 = np.array([[1, -1e-9, 0], [1e-9, 1, 0], [0, 0, 1]])
    assert_allclose(dcm.from_llw(*llw2), A2, rtol=1e-10, atol=1e-10)

    llw3 = np.array([-30, -45, 90])
    A3 = np.array([[np.sqrt(2)/4, -np.sqrt(2)/2, np.sqrt(6)/4],
                   [-np.sqrt(2)/4, -np.sqrt(2)/2, -np.sqrt(6)/4],
                   [np.sqrt(3)/2, 0, -0.5]])

    assert_allclose(dcm.from_llw(*llw3), A3, rtol=1e-10, atol=1e-10)

    A4 = np.array([[2**0.5/2, 2**0.5/4, 6**0.5/4],
                   [2**0.5/2, -2**0.5/4, -6**0.5/4],
                   [0, 3**0.5/2, -0.5]])
    assert_allclose(dcm.from_llw(*llw3[:2]), A4, rtol=1e-10, atol=1e-10)

    llw = np.empty((15, 3))
    llw[:5] = llw1
    llw[5:10] = llw2
    llw[10:] = llw3
    A = np.empty((15, 3, 3))
    A[:5] = A1
    A[5:10] = A2
    A[10:] = A3
    assert_allclose(dcm.from_llw(*llw.T), A, rtol=1e-10, atol=1e-10)


def test_to_llw():
    A1 = np.identity(3)
    llw1 = np.array([90, 0, -90])
    assert_allclose(dcm.to_llw(A1), llw1, rtol=1e-10)

    A2 = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    llw2 = np.array([0, 0, 0])
    assert_allclose(dcm.to_llw(A2), llw2, atol=1e-10)

    A = np.empty((10, 3, 3))
    A[:5] = A1
    A[5:] = A2
    llw = np.empty((10, 3))
    llw[:5] = llw1
    llw[5:] = llw2

    ret = dcm.to_llw(A)
    for i in range(3):
        assert_allclose(ret[i], llw[:, i], rtol=1e-10, atol=1e-10)


def test_dcm_llw_conversion():
    rng = np.random.RandomState(0)

    lat = rng.uniform(-90, 90, 20)
    lon = rng.uniform(-180, 180, 20)
    wan = rng.uniform(-180, 180, 20)

    A = dcm.from_llw(lat, lon, wan)
    lat_r, lon_r, wan_r = dcm.to_llw(A)

    assert_allclose(lon_r, lon, rtol=1e-10)
    assert_allclose(lat_r, lat, rtol=1e-10)
    assert_allclose(wan_r, wan, rtol=1e-10)


def test_dcm_Spline():
    ht = [0, 45, 90]
    C = dcm.from_hpr(ht, 0, 0)
    t = [0, 45, 90]
    s = dcm.Spline(t, C)

    t_test = [0, 30, 60, 90]
    C_test = s(t_test)
    h, p, r = dcm.to_hpr(C_test)
    assert_allclose(h, [0, 30, 60, 90], rtol=1e-14, atol=1e-16)
    assert_allclose(p, 0, atol=1e-16)
    assert_allclose(r, 0, atol=1e-16)

    omega = np.rad2deg(s(t_test, 1))
    assert_allclose(omega[:, 0], 0, atol=1e-16)
    assert_allclose(omega[:, 1], 0, atol=1e-6)
    assert_allclose(omega[:, 2], -1)

    beta = np.rad2deg(s(t_test, 2))
    assert_allclose(beta, 0, atol=1e-16)

    t = np.linspace(0, 100, 101)
    ht = 10 * t + 5 * np.sin(2 * np.pi * t / 10)
    pt = 7 * t + 3 * np.sin(2 * np.pi * t / 10 + 2)
    rt = -3 * t + 3 * np.sin(2 * np.pi * t / 10 - 2)
    C = dcm.from_hpr(ht, pt, rt)
    s = dcm.Spline(t, C)

    Cs = s(t[::-1])
    assert_allclose(Cs[::-1], C)


def test_match_vectors():
    Cab_true = dcm.from_hpr(20, -10, 5)
    vb = np.array([
        [0, 1, 0],
        [0, 0, 1]
    ])
    va = vb.dot(Cab_true.T)

    Cab = dcm.match_vectors(va, vb)
    assert_allclose(Cab, Cab_true, atol=1e-16)

    Cab = dcm.match_vectors(va, vb, [200, 1])
    assert_allclose(Cab, Cab_true, atol=1e-16)

    rng = np.random.RandomState(0)
    vb = rng.rand(100, 3)
    vb /= np.linalg.norm(vb, axis=1)[:, None]
    va = vb.dot(Cab_true.T)
    Cab = dcm.match_vectors(va, vb)
    assert_allclose(Cab, Cab_true, atol=1e-16)


if __name__ == '__main__':
    run_module_suite()
