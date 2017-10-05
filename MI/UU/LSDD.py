import numpy as np
import MI

def r(x):
  return x.sum(axis=1).reshape(-1, 1)

def LSDD(P, Q, s, l):
  X = np.vstack((P, Q))
  H = np.exp(- (r(X**2) - 2*X.dot(X.T) + r(X**2).T) / (2*s**2))
  h = np.exp(- (r(X**2) - 2*X.dot(P.T) + r(P**2).T) / (2*s**2)).mean(axis=1) \
    - np.exp(- (r(X**2) - 2*X.dot(Q.T) + r(Q**2).T) / (2*s**2)).mean(axis=1)
  t = np.linalg.solve(H + l * np.eye(H.shape[0]), h)
  return t

def train(bags, width, reg, args):
  P = np.vstack(MI.extract_bags(bags, 1))
  Q = np.vstack(MI.extract_bags(bags, 0))

  t = LSDD(P, Q, width, reg)
  X = np.vstack((P, Q))

  def classifier(x):
    x = x.reshape(1, -1)
    return t.T.dot(np.exp(- (r(X**2) - 2*X.dot(x.T) + r(x**2).T) / (2*width**2)))

  return lambda X: np.max([classifier(x) for x in X])
