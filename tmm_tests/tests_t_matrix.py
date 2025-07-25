import torch
import numpy as np
import time
from torch_tmm.t_matrix import T_matrix

def run_comprehensive_prop_test(device=torch.device('cpu')):
    wavelengths = torch.linspace(400, 800, 401)
    angles = torch.linspace(0, 89, 90)

    dtype = torch.complex64

    #First prop test (n_env = 1 and n_layer = 1)
    n_env = 1*torch.ones_like(wavelengths)
    n_layer = 1*torch.ones_like(wavelengths)
    d_layer = torch.tensor(30)

    test_prop1 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=dtype, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop1:
        raise ValueError('Failed test_prop1')
    
    #second prop test (n_env = 1 and n_layer = 3 + 1j)
    n_env = 1*torch.ones_like(wavelengths)
    n_layer = (3 + 1j)*torch.ones_like(wavelengths)
    d_layer = torch.tensor(10)

    test_prop2 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=dtype, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop2:
        raise ValueError('Failed test_prop2')
    
    #third prop test (n_env = 3 + 1j and n_layer = 1)
    n_env = (3 + 1j)*torch.ones_like(wavelengths)
    n_layer = 1*torch.ones_like(wavelengths)
    d_layer = torch.tensor(50)

    test_prop3 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=dtype, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop3:
        raise ValueError('Failed test_prop3')
    
    #Fourth prop test (n_env = 3 + 1j and n_layer = 4 + 8j)
    n_env = (3 + 1j)*torch.ones_like(wavelengths)
    n_layer = (4 + 8j)*torch.ones_like(wavelengths)
    d_layer = torch.tensor(50)

    test_prop4 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=dtype, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop4:
        raise ValueError('Failed test_prop4')
    
    #Fifth prop test (alpha > 60)
    n_env = 1*torch.ones_like(wavelengths)
    n_layer = (3 + 1j)*torch.ones_like(wavelengths)
    d_layer = torch.tensor(6000000)

    test_prop5 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=dtype, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop5:
        raise ValueError('Failed test_prop5')
    
    #Sixth prop test (n_env = 3 + 1j and n_layer = 1, d = 20000, complex128)
    n_env = (3 + 1j)*torch.ones_like(wavelengths)
    n_layer = 1*torch.ones_like(wavelengths)
    d_layer = torch.tensor(20000)

    test_prop6 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=torch.complex128, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop6:
        raise ValueError('Failed test_prop6')
    
    #seventh prop test (n_env = 4 + 2j and n_layer = (0.1 + 5j), d = 10000, complex128)
    n_env = (4 + 2j)*torch.ones_like(wavelengths)
    n_layer = (0.1 + 5j)*torch.ones_like(wavelengths)
    d_layer = torch.tensor(10000)

    test_prop7 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=torch.complex128, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop7:
        raise ValueError('Failed test_prop7')
    
    #eight prop test (n_env = 4 - 2j and n_layer = (0.1 - 5j), d = 0)
    n_env = (4 - 2j)*torch.ones_like(wavelengths)
    n_layer = (0.1 - 5j)*torch.ones_like(wavelengths)
    d_layer = torch.tensor(0)

    test_prop8 = prop_test(wavelengths, angles, n_layer, d_layer, n_env,
                            dtype=dtype, device=device, threshold=1e-10,
                            verbose=False)
    
    if not test_prop8:
        raise ValueError('Failed test_prop8')
    
    print('All the tests are passed!')


def single_layer_test(wavelengths: torch.Tensor,
                        angles: torch.Tensor, 
                        pol: str,
                        n: torch.Tensor, 
                        d: torch.Tensor, 
                        n_env: torch.Tensor,
                        n_subs: torch.Tensor,
                        dtype: torch.dtype = torch.complex64,
                        device: torch.device = torch.device('cpu'),
                        verbose: bool = False) -> str:
    '''
    Test the Transfer matrix for a single layer.

    Parameters
    ----------
    wavelengths : torch.Tensor
        Wavelengths to test.
    angles : torch.Tensor
        Angles to test.
    pol : str
        Polarization to test.
    n : torch.Tensor
        Refractive index of the layer.
    d : torch.Tensor
        Thickness of the layer.
    n_env : torch.Tensor
        Refractive index of the environment    
    n_subs : torch.Tensor
        Refractive index of the substrate   
    dtype : torch.dtype, optional
        Data type of the tensors, by default torch.complex64
    device : torch.device, optional
        Device to run the tensors on, by default torch.device('cpu')
    '''
    #Transfer input data to the correct device and data type
    wavelengths = wavelengths.to(dtype).to(device)
    angles = angles.to(dtype).to(device)
    n = n.to(dtype).to(device)
    d = d.to(dtype).to(device)
    n_env = n_env.to(dtype).to(device)
    n_subs = n_subs.to(dtype).to(device)
    n_air = torch.ones_like(n).to(dtype).to(device)

    assert wavelengths.ndim == 1, 'Wavelengths must be a 1D tensor'
    assert angles.ndim == 1, 'Angles must be a 1D tensor'
    assert pol in ['s', 'p'], 'Polarization must be either s or p'
    assert n.ndim == 1, 'Refractive index must be a 1D tensor'
    assert d.ndim == 0, 'Thickness must be a scalar tensor'
    assert n_env.ndim == 1, 'Refractive index of the environment must be a 1D tensor'
    assert n_subs.ndim == 1, 'Refractive index of the substrate must be a 1D tensor'
    assert wavelengths.shape[0] == n_env.shape[0], 'Wavelengths and refractive index of the environment must have the same length'
    assert wavelengths.shape[0] == n_subs.shape[0], 'Wavelengths and refractive index of the substrate must have the same length'
    assert wavelengths.shape[0] == n.shape[0], 'Wavelengths and refractive index must have the same length'

    #T matrix method
    start = time.time()
    Tm_obj = T_matrix(dtype=dtype, device=device)
    nx = n_env[:, None] * torch.sin(angles[None, :])
    T_layer = Tm_obj.coherent_layer(pol, n, d, wavelengths, nx)
    if pol == 's':
        T_env = Tm_obj.interface_s(n_env, n_air, nx)
        T_subs = Tm_obj.interface_s(n_air, n_subs, nx)
    else:
        T_env = Tm_obj.interface_p(n_env, n_air, nx)
        T_subs = Tm_obj.interface_p(n_air, n_subs, nx)

    
    Tm = torch.einsum('...ij,...jk->...ik', T_env, torch.einsum('...ij,...jk->...ik', T_layer, T_subs ))

    t = 1/Tm[:, :, 0, 0]
    r = Tm[:, :, 1, 0]/Tm[:, :, 0, 0]
    end = time.time()

    #Analytical method
    n1z = torch.sqrt(n_env[:, None]**2 - nx**2)
    n2z = torch.sqrt(n[:,None]**2 - nx**2)
    n3z = torch.sqrt(n_subs[:, None]**2 - nx**2)
    beta = 2*np.pi/wavelengths[:, None]*n2z*d

    if pol == 's':
        r12 = (n1z - n2z)/(n1z + n2z)
        r23 = (n2z - n3z)/(n2z + n3z)
        t12 = 2*n1z/(n1z + n2z)
        t23 = 2*n2z/(n2z + n3z)
    else:
        r12 = (n[:,None]**2*n1z - n_env[:,None]**2*n2z)/(n[:,None]**2*n1z + n_env[:,None]**2*n2z)
        r23 = (n_subs[:,None]**2*n2z - n[:,None]**2*n3z)/(n_subs[:,None]**2*n2z + n[:,None]**2*n3z)
        t12 = 2*n_env[:,None]*n[:,None]*n1z/(n[:,None]**2*n1z + n_env[:,None]**2*n2z)
        t23 = 2*n[:,None]*n_subs[:,None]*n2z/(n_subs[:,None]**2*n2z + n[:,None]**2*n3z)

    r_analytical = (r12 + r23*torch.exp(2j*beta))/(1 + r12*r23*torch.exp(2j*beta))
    t_analytical = t12*t23*torch.exp(1j*beta)/(1 + r12*r23*torch.exp(2j*beta))

    MSE_r = torch.mean(torch.abs(r - r_analytical)**2)
    MSE_t = torch.mean(torch.abs(t - t_analytical)**2)

    condition = MSE_r < 1e-8 and MSE_t < 1e-8

    if not verbose:
        return True if condition else False
    else:
        return f"The single_layer_test for pol:'{pol}' {'passed' if condition else 'failed'} in {end - start} seconds, MSE_r: {MSE_r}, MSE_t: {MSE_t}"

def coherent_layer_test(wavelengths: torch.Tensor,
                        angles: torch.Tensor, 
                        pol: str,
                        n: torch.Tensor, 
                        d: torch.Tensor, 
                        n_env: torch.Tensor,
                        dtype: torch.dtype = torch.complex64,
                        device: torch.device = torch.device('cpu'),
                        verbose: bool = False) -> str:
    '''
    Test the Transfer matrix for a single layer.

    Parameters
    ----------
    wavelengths : torch.Tensor
        Wavelengths to test.
    angles : torch.Tensor
        Angles to test.
    pol : str
        Polarization to test.
    n : torch.Tensor
        Refractive index of the layer.
    d : torch.Tensor
        Thickness of the layer.
    n_env : torch.Tensor
        Refractive index of the environment    
    dtype : torch.dtype, optional
        Data type of the tensors, by default torch.complex64
    device : torch.device, optional
        Device to run the tensors on, by default torch.device('cpu')
    '''
    #Transfer input data to the correct device and data type
    wavelengths = wavelengths.to(dtype).to(device)
    angles = angles.to(dtype).to(device)
    n = n.to(dtype).to(device)
    d = d.to(dtype).to(device)
    n_env = n_env.to(dtype).to(device)

    assert wavelengths.ndim == 1, 'Wavelengths must be a 1D tensor'
    assert angles.ndim == 1, 'Angles must be a 1D tensor'
    assert pol in ['s', 'p'], 'Polarization must be either s or p'
    assert n.ndim == 1, 'Refractive index must be a 1D tensor'
    assert d.ndim == 0, 'Thickness must be a scalar tensor'
    assert n_env.ndim == 1, 'Refractive index of the environment must be a 1D tensor'
    assert wavelengths.shape[0] == n_env.shape[0], 'Wavelengths and refractive index of the environment must have the same length'
    assert wavelengths.shape[0] == n.shape[0], 'Wavelengths and refractive index must have the same length'

    #T matrix method
    start = time.time()
    Tm_obj = T_matrix(dtype=dtype, device=device)
    nx = n_env[:, None] * torch.sin(angles[None, :])
    T_layer = Tm_obj.coherent_layer(pol, n, d, wavelengths, nx)
    
    t = 1/T_layer[:, :, 0, 0]
    r = T_layer[:, :, 1, 0]/T_layer[:, :, 0, 0]
    end = time.time()

    #Analytical method
    n_air = torch.ones_like(n).to(dtype).to(device)
    n1z = torch.sqrt(n_air[:, None]**2 - nx**2)
    n2z = torch.sqrt(n[:,None]**2 - nx**2)
    beta = 2*np.pi/wavelengths[:, None]*n2z*d

    if pol == 's':
        r12 = (n1z - n2z)/(n1z + n2z)
        r23 = (n2z - n1z)/(n2z + n1z)
        t12 = 2*n1z/(n1z + n2z)
        t23 = 2*n2z/(n1z + n2z)
    else:
        r12 = (n[:,None]**2*n1z - n_air[:,None]**2*n2z)/(n[:,None]**2*n1z + n_air[:,None]**2*n2z)
        r23 = (n_air[:,None]**2*n2z - n[:,None]**2*n1z)/(n_air[:,None]**2*n2z + n[:,None]**2*n1z)
        t12 = 2*n[:,None]**2*n1z/(n[:,None]**2*n1z + n_air[:,None]**2*n2z)
        t23 = 2*n_air[:,None]**2*n2z/(n_air[:,None]**2*n2z + n[:,None]**2*n1z)

    r_analytical = (r12 + r23*torch.exp(2j*beta))/(1 + r12*r23*torch.exp(2j*beta))
    t_analytical = t12*t23*torch.exp(1j*beta)/(1 + r12*r23*torch.exp(2j*beta))

    MSE_r = torch.mean(torch.abs(r - r_analytical)**2)
    MSE_t = torch.mean(torch.abs(t - t_analytical)**2)

    condition = MSE_r < 1e-8 and MSE_t < 1e-8

    if not verbose:
        return True if condition else False
    else:
        return f"The coherent_layer_test for pol:'{pol}' {'passed' if condition else 'failed'} in {end - start} seconds, MSE_r: {MSE_r}, MSE_t: {MSE_t}"

def prop_test(wavelengths: torch.Tensor, 
              angles: torch.Tensor, 
              n: torch.Tensor, 
              d: torch.Tensor, 
              n_env: torch.Tensor,
              dtype: torch.dtype = torch.complex64,
              device: torch.device = torch.device('cpu'),
              threshold: float = 1e-10,
              verbose: bool = False) -> str:
    '''
    Test the propagation matrix for a single layer.

    Parameters
    ----------
    wavelengths : torch.Tensor
        Wavelengths to test.
    angles : torch.Tensor
        Angles to test.
    n : torch.Tensor
        Refractive index of the layer.
    d : torch.Tensor
        Thickness of the layer.
    n_env : torch.Tensor
        Refractive index of the environment    
    dtype : torch.dtype, optional
        Data type of the tensors, by default torch.complex64
    device : torch.device, optional
        Device to run the tensors on, by default torch.device('cpu')
    '''
    #Transfer input data to the correct device and data type
    wavelengths = wavelengths.to(dtype).to(device)
    angles = angles.to(dtype).to(device)
    n = n.to(dtype).to(device)
    d = d.to(dtype).to(device)

    assert wavelengths.ndim == 1, 'Wavelengths must be a 1D tensor'
    assert angles.ndim == 1, 'Angles must be a 1D tensor'
    assert n.ndim == 1, 'Refractive index must be a 1D tensor'
    assert d.ndim == 0, 'Thickness must be a scalar tensor'
    assert n_env.ndim == 1, 'Refractive index of the environment must be a 1D tensor'
    assert wavelengths.shape[0] == n_env.shape[0], 'Wavelengths and refractive index of the environment must have the same length'
    assert wavelengths.shape[0] == n.shape[0], 'Wavelengths and refractive index must have the same length'
    #assert n_env.imag.all() >= 0

    #T matrix method
    start = time.time()
    Tm_obj = T_matrix(dtype=dtype, device=device)
    nx = n_env[:, None] * torch.sin(angles[None, :])
    T_prop = Tm_obj.propagation_coherent(n, d, wavelengths, nx)
    t = 1/T_prop[:, :, 0, 0]
    end = time.time()
    
    #Analytical approach
    niz = torch.sqrt(n[:, None]**2 - nx**2)
    delta = 2*torch.pi/wavelengths[:, None]*niz*d
    # -- Split into phase (φ) and attenuation (α d) -----------------------
    phi   = delta.real                                    # phase
    alpha = (delta.imag.abs()).clamp(max=60.0)          # ensure αd ≤ clamp_alpha

    delta = phi + 1j*alpha
  
    # torch.polar(r, θ)  returns  r·e^{iθ}
    t_analytical  = torch.exp(1j*delta)
    
    #Check if the two methods are the same
    MSE = (torch.mean(torch.abs(t - t_analytical)**2)).item()
    condition = MSE < threshold

    if not verbose:
        return True if condition else False
    else:
        return f"The prop_test {'passed' if condition else 'failed'} in {end - start} seconds, MSE: {MSE}"
    
def interface_test(angles: torch.Tensor, 
                ni: torch.Tensor, 
                nf: torch.Tensor,
                n_env: torch.Tensor,
                pol: str = 's',
                dtype: torch.dtype = torch.complex64,
                device: torch.device = torch.device('cpu'),
                verbose: bool = False) -> str:
    """
    Test the interface reflection and transmission coefficients

    Parameters
    ----------
    angles : torch.Tensor
        Angles to test.
    ni : torch.Tensor
        Refractive index of the current layer.
    nf : torch.Tensor
        Refractive index of the next layer.
    n_env : torch.Tensor
        Refractive index of the environment  
    pol : str, optional
        Polarization to test, by default
        's' for s-polarization and 'p' for p-polarization  
    dtype : torch.dtype, optional
        Data type of the tensors, by default torch.complex64
    device : torch.device, optional
        Device to run the tensors on, by default torch.device('cpu')
    """
    #Transfer input data to the correct device and data type
    n_env = n_env.to(dtype).to(device)
    ni = ni.to(dtype).to(device)
    nf = nf.to(dtype).to(device)
    angles = angles.to(dtype).to(device)

    assert angles.ndim == 1, 'Angles must be a 1D tensor'
    assert n_env.ndim == 1, 'Refractive index of the environment must be a 1D tensor'
    assert ni.ndim == 1, 'Refractive index of the environment must be a 1D tensor'
    assert nf.ndim == 1, 'Refractive index of the environment must be a 1D tensor'
    assert ni.shape[0] == n_env.shape[0], 'Wavelengths and refractive index of the environment must have the same length'
    assert ni.shape[0] == nf.shape[0], 'Wavelengths and refractive index must have the same length'
    assert pol in ['s', 'p'], 'Polarization must be either s or p'

    #T matrix method
    start = time.time()
    Tm_obj = T_matrix(dtype=dtype, device=device)
    nx = n_env[:, None] * torch.sin(angles[None, :])
    if pol == 's':
        T_int = Tm_obj.interface_s(ni, nf, nx)
    else:
        T_int = Tm_obj.interface_p(ni, nf, nx)
    
    t = 1/T_int[:, :, 0, 0]
    r = T_int[:, :, 1, 0]/T_int[:, :, 0, 0]
    end = time.time()

    #Analytical method
    niz = torch.sqrt(ni[:,None]**2 - nx**2)
    nfz = torch.sqrt(nf[:,None]**2 - nx**2)

    if pol == 's':
        r_analytical = (niz - nfz)/(niz + nfz)
        t_analytical = 2*niz/(niz + nfz)
    else:
        r_analytical = (nf[:,None]**2*niz - ni[:,None]**2*nfz)/(nf[:,None]**2*niz + ni[:,None]**2*nfz)
        t_analytical = 2*ni[:,None]*nf[:,None]*niz/(nf[:,None]**2*niz + ni[:,None]**2*nfz)

    MSE_r = torch.mean(torch.abs(r - r_analytical)**2)
    MSE_t = torch.mean(torch.abs(t - t_analytical)**2)

    condition = MSE_r < 1e-8 and MSE_t < 1e-8

    if not verbose:
        return True if condition else False
    else:
        return f"The interface_test for pol:'{pol}' {'passed' if condition else 'failed'} in {end - start} seconds, MSE_r: {MSE_r}, MSE_t: {MSE_t}"
    

if __name__ == '__main__':
    #run_comprehensive_prop_test(device=torch.device('cpu'))
    wavelengths = torch.linspace(400, 800, 401)
    angles = torch.linspace(0, 89, 90)

    n = 1*torch.ones_like(wavelengths)
    n_env = 1*torch.ones_like(wavelengths)
    n_subs = 1*torch.ones_like(wavelengths)
    d = torch.tensor(1000000000)

    dtype = torch.complex64
    test = single_layer_test(wavelengths, angles, 'p', n, d, n_env, n_subs,
                      dtype=dtype, verbose=True)
    print(test)