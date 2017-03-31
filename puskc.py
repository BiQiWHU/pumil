#!/usr/bin/env python
# coding: utf-8

import itertools
import argparse
import MI
import numpy as np

def train_pu_skc(data, args):
  degs = [1, 2, 3]
  regs = [1.0e+03, 1.0, 1.0e-03, 1.0e-06]

  def train(data, deg, reg):
    bdim = len(data)
    theta = MI.PU.class_prior(data, degree = 1, reg = 1.0e+05)
    basis = MI.kernel.minimax_basis(data, deg)
    model = MI.PU.SKC.train(data, basis, bdim, theta, reg, args)
    metadata = {'theta': theta, 'reg': reg, 'degree': deg}
    return model, metadata

  # cross validation
  best_param = {}
  best_error = np.inf
  if args.verbose:
    print("# *** Cross Validation ***")
  for deg, reg in itertools.product(degs, regs):
    try:
      errors = []
      for data_train, data_val in MI.cross_validation(data, 5):
        clf, metadata = train(data_train, deg, reg)
        e = MI.PU.prediction_error(data_val, clf, metadata['theta'])
        errors.append(e)

      error = np.mean(errors)

      if args.verbose:
        print("#  degree = {} / reg = {:.3e} : theta = {:.3e} / error = {:.3e}".format(deg, reg, metadata['theta'], error))

      if error < best_error:
        best_param = {'degree': deg, 'reg': reg}

    except ValueError:
      # sometimes fails for large degree
      print("#  degree = {} / reg = {:.3e} : error = NaN".format(deg, reg))

  if args.verbose:
    print("# {}".format('-'*80))

  # training using the best parameter
  model, metadata = train(data, best_param['degree'], best_param['reg'])

  if args.verbose:
    print("#  estimated class prior = {:.6f}".format(metadata['theta']))

  return model, best_param


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="PU-SKC experiment toolkit")

  parser.add_argument('--dataset',
      action   = 'store',
      required = True,
      type     = str,
      help     = 'multiple instance dataset')

  parser.add_argument('--prior',
      action   = 'store',
      default  = 0.1,
      type     = float,
      metavar  = '[0-1]',
      help     = 'class prior (the ratio of positive data)')

  parser.add_argument('--loss',
      action   = 'store',
      default  = 'double_hinge',
      type     = str,
      metavar  = ['double_hinge', 'squared'],
      help     = 'loss function')

  parser.add_argument('-v', '--verbose',
      action   = 'store_true',
      default  = False,
      help     = 'verbose output')

  parser.add_argument('--aucplot',
      action   = 'store_true',
      default  = False,
      help     = 'output prediction score and true label for AUC plot')

  args = parser.parse_args()

  print("# {}".format('-'*80))
  print("# *** Experimental Setting ***")
  print("#   model                     : PU-SKC (loss function = {})".format(args.loss))
  print("#   basis                     : minimax")
  print("#   validation                : 5 fold cross validation")
  print("# {}".format('-'*80))

  bags_train, bags_test, metadata = MI.datasets.load_dataset(args.dataset, args.prior)
  clf, best_param = train_pu_skc(bags_train, args)
  print("#  degree = {} / reg = {:.3e}".format(best_param['degree'], best_param['reg']))
  MI.print_evaluation_result(clf, bags_test, args)
