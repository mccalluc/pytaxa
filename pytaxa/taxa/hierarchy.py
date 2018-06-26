from ..utils import *
from ..ranks_ref import *
from .taxon import Taxon
from ..constructors import *

class Hierarchy(object):
    """
    Hierarchy class

    Stores one or more `taxon` objects. Prints first 10 taxa 
    for brevity sake.

    Usage:::
        
        from pytaxa import constructors as cs
        from pytaxa import Taxon

        # database to use for many taxon's
        db = cs.taxon_database("ncbi", 
            "http://www.ncbi.nlm.nih.gov/taxonomy",
            "NCBI Taxonomy Database", 
            "*")
        
        # make some taxon's
        tx1 = Taxon(cs.taxon_name("Poaceae"), 
          cs.taxon_rank("family", "ncbi"), cs.taxon_id(4479, db))
        tx2 = Taxon(cs.taxon_name("Poa"), 
          cs.taxon_rank("genus", "ncbi"), cs.taxon_id(12345, db))
        tx3 = Taxon(cs.taxon_name("Poa annua"), 
          cs.taxon_rank("species", "ncbi"), cs.taxon_id(93036, db))
        
        # single taxon
        from pytaxa import Hierarchy
        Hierarchy(tx1)

        # many taxon's
        z = Hierarchy(tx3, tx1, tx2)
        z
        z.taxa
        z.ranklist

        # various accessors
        ## length - i.e., number of taxa
        z.xlen
        len(z)

        # empty Hierarchies
        Hierarchy(Taxon({}))

        # pop, pick, span
        ## example Hierarchy objects
        from pytaxa import examples
        examples.eg_hierarchy("poa")
        examples.eg_hierarchy("puma")
        examples.eg_hierarchy("salmo")
        
        ## pop
        ex = examples.eg_hierarchy("salmo")
        ex.pop(ranks = "family")
        ex.pop(names = "Salmo")
        ex.pop(ids = 331030)

        ## pick
        ex = examples.eg_hierarchy("salmo")
        ex
        ex.pick(ranks = "family")
        ex.pick(names = ["Salmo", "Chordata", "Teleostei"])
        ex.pick(ids = 331030)
    """
    def __init__(self, *x: Taxon):
      super(Hierarchy, self).__init__()
      self.x = x
      self.ranklist = None
      self.xlen = len(x)
      all_have_ranks = no_nones([z.rank.get("name") for z in x])
      if all_have_ranks:
        self.taxa = self.__sort_hierarchy(x)
      else:
        self.taxa = x

    def __repr__(self):
      hier = "<Hierarchy>\n  "
      if len(self.taxa) == 0:
        txt = "Empty hierarchy\n  "
      elif self.taxa[0].is_empty(): 
        txt = "Empty hierarchy\n  "
      else:
        z = [self.print_taxon(z) for z in self.taxa[:10]]
        no_taxa = "no. taxon's: %d\n  " % len(self.taxa)
        txt = '\n  '.join(z)
      return hier + txt

    def __len__(self):
      return self.xlen

    @staticmethod
    def print_taxon(x):
      if all(b is None for b in x.name.values()): 
        return "empty"
      else:
        return ' / '.join([
          str(x.name.get('name')) or "", 
          str(x.rank.get('name')) or "",
          str(x.id.get('id')) or ""
        ])

    def __sort_hierarchy(self, x):
      if (len(x) == 0):
        return(x)
      ranks = [z.rank.get("name") for z in x]
      for w in ranks:
        if w not in self.__poss_ranks():
          raise ValueError(w + " not in the acceptable set of rank names")
      self.ranklist = list(unique(flatten([ which_ranks(f) for f in ranks ])))
      return [x[i] for i in argsort(self.ranklist)]

    @staticmethod
    def __poss_ranks():
      rks = ranks_ref()
      allrks = [x.split(',') for x in rks.values()]
      tmp = list(set(flatten(allrks)))
      tmp.sort()
      return tmp

    @staticmethod
    def __all_empty(x):
      return all([z.is_empty() for z in x])

    def pop(self, ranks = None, names = None, ids = None):
      if self.__all_empty(self.taxa):
        raise ValueError("no taxa found")
      
      alldat = [ranks, names, ids]
      if (len(alldat) == 0):
        raise ValueError("one of 'ranks', 'names', or 'ids' must be used")
      
      taxa_rks = [z.rank.get('name') for z in self.taxa]
      taxa_nms = [z.name.get('name') for z in self.taxa]
      taxa_ids = [z.id.get('id') for z in self.taxa]

      self.taxa = [w for w in self.taxa if 
        w.rank.get('name') != ranks and 
        w.name.get('name') != names and 
        w.id.get('id') != ids]

      self.taxa = self.__sort_hierarchy(self.taxa)
      self.xlen = len(self.taxa)
      return self

    def pick(self, ranks = None, names = None, ids = None):
      if self.__all_empty(self.taxa):
        raise ValueError("no taxa found")
      
      alldat = [ranks, names, ids]
      if (len(alldat) == 0):
        raise ValueError("one of 'ranks', 'names', or 'ids' must be used")
      
      self.taxa = [
        w for w in self.taxa if self.__inbool(w.rank.get('name'), ranks) or self.__inbool(w.name.get('name'), names) or self.__inbool(w.id.get('id'), int2str(ids))
      ]

      self.taxa = self.__sort_hierarchy(self.taxa)
      self.xlen = len(self.taxa)
      return self

    @staticmethod
    def __inbool(x, y):
      # flatten list, ints converted to str
      x = str(x) if isinstance(x, int) else x
      x = [x]
      return False if x is None or y is None else any([z for z in x if z in y])
      