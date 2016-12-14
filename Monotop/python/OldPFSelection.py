from PandaCore.Tools.Misc import *
from re import sub

triggers = {
    'met':'(trigger&1)!=0',
    'ele':'(trigger&2)!=0',
    'pho':'(trigger&4)!=0',
}

metFilter='metFilter==1'
topTagSF = '%f*(fj1IsMatched==1)+%f*(fj1IsMatched==0)'%(1.,1.)
ak4bTagSF = 'sf_btag0*(isojetNBtags==0)+sf_btag1*(isojetNBtags==1)+1*(isojetNBtags>1)'


presel = 'nFatjet==1 && fj1Pt>250 && TMath::Abs(fj1Eta)<2.4 && 110<fj1MSD && fj1MSD<210 && fj1Tau32<0.6'
cuts = {
    # analysis regions
    'signal_nobtag'     : tAND(metFilter,tAND(presel,'pfmet>250 && dphipfmet>1.1 && (nLooseMuon+nLooseElectron+nLoosePhoton+nTau)==0')), # turning off btags
    'signal'            : tAND(metFilter,tAND(presel,'pfmet>250 && dphipfmet>1.1 && (nLooseMuon+nLooseElectron+nLoosePhoton+nTau)==0 && fj1MaxCSV>0.46 && isojetNBtags==0')),
    # 'signal_nomf'       : tAND(presel,'met>175 && puppimet>250 && dphipuppimet>1.1 && (nLooseMuon+nLooseElectron+nLoosePhoton+nTau)==0 && fj1MaxCSV>0.46 && isojetNBtags==0 && fj1isTight==1 && TMath::Abs(met-calomet)/puppimet<0.5'),
    'singlemuontop'     : tAND(metFilter,tAND(presel,'pfUWmag>250 && (nLooseElectron+nLoosePhoton+nTau)==0 && nLooseMuon==1 && looseLep1IsTight==1 && fj1MaxCSV>0.46 && isojetNBtags==1')),
    'singleelectrontop' : tAND(metFilter,tAND(presel,'pfUWmag>250 && (nLooseMuon+nLoosePhoton+nTau)==0 && nLooseElectron==1 && looseLep1IsTight==1 && fj1MaxCSV>0.46 && isojetNBtags==1 && pfmet>40')),
    'singlemuonw'       : tAND(metFilter,tAND(presel,'pfUWmag>250 && (nLooseElectron+nLoosePhoton+nTau)==0 && nLooseMuon==1 && looseLep1IsTight==1 && fj1MaxCSV<0.46 && isojetNBtags==0')),
    'singleelectronw'   : tAND(metFilter,tAND(presel,'pfUWmag>250 && (nLooseMuon+nLoosePhoton+nTau)==0 && nLooseElectron==1 && looseLep1IsTight==1 && fj1MaxCSV<0.46 && isojetNBtags==0 && pfmet>40')),
    'singlemuon'        : tAND(metFilter,tAND(presel,'pfUWmag>250 && (nLooseElectron+nLoosePhoton+nTau)==0 && nLooseMuon==1 && looseLep1IsTight==1')),
    'singleelectron'    : tAND(metFilter,tAND(presel,'pfUWmag>250 && (nLooseMuon+nLoosePhoton+nTau)==0 && nLooseElectron==1 && looseLep1IsTight==1 && pfmet>40')),
    'dimuon'            : tAND(metFilter,tAND(presel,'pfUZmag>250 && (nLooseElectron+nLoosePhoton+nTau)==0 && nLooseMuon==2 && looseLep1IsTight==1')),
    'dielectron'        : tAND(metFilter,tAND(presel,'pfUZmag>250 && (nLooseMuon+nLoosePhoton+nTau)==0 && nLooseElectron==2 && looseLep1IsTight==1')),
    'photon'            : tAND(metFilter,tAND(presel,'pfUAmag>250 && (nLooseMuon+nLooseElectron+nTau)==0 && nLoosePhoton==1 && loosePho1IsTight==1')),
}

tag_presel = removeCut(removeCut(tOR(cuts['singlemuontop'],cuts['singleelectrontop']),'fj1Tau32'),'fj1MSD')
mistag_presel = tAND(removeCut(removeCut(cuts['photon'],'fj1Tau32'),'fj1MSD'),'fj1MSD>40')
tag = 'fj1Tau32<0.61 && 110<fj1MSD && fj1MSD<210'
tt_cuts = {
  'tag' : tag_presel,
  'tag_pass' : tAND(tag,tag_presel),
  'tag_fail' : tAND(tNOT(tag),tag_presel),
  'mistag' : mistag_presel,
  'mistag_pass' : tAND(tag,mistag_presel),
  'mistag_fail' : tAND(tNOT(tag),mistag_presel),
}

weights = {
    # analysis weights
  'signal_nobtag'    : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
  'signal'    : tTIMES(tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV*sf_sjbtag1',topTagSF),ak4bTagSF),
  'top'       : tTIMES(tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV*sf_sjbtag1',topTagSF),ak4bTagSF),
  'w'         : tTIMES(tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV*sf_sjbtag0',topTagSF),ak4bTagSF),
  #'notag'     : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
  'notag'     : tTIMES('%f*normalizedWeight*sf_pu*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
  'singleelectron' : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
  'singlemuon'     : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
}

for x in ['singlemuontop','singleelectrontop']:
  weights[x] = weights['top']
for x in ['singlemuonw','singleelectronw']:
  weights[x] = weights['w']
for x in ['dimuon','dielectron']:
  if x=='dielectron':
    weights[x] = tTIMES('sf_lep',weights['notag'])
  else:
    weights[x] = weights['notag']
for x in ['photon']:
  #weights[x] = weights['notag']
  weights[x] = tTIMES('sf_pho',weights['notag'])

'''
weights = {
    # analysis weights
  #'signal'    : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF), # no btags
  'signal'    : tTIMES(tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV*sf_sjbtag1',topTagSF),ak4bTagSF),
  'top'       : tTIMES(tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV*sf_sjbtag1',topTagSF),ak4bTagSF),
  'w'         : tTIMES(tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV*sf_sjbtag0',topTagSF),ak4bTagSF),
  'notag'     : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
  'singleelectron' : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
  'singlemuon'     : tTIMES('%f*normalizedWeight*sf_pu*sf_lep*sf_ewkV*sf_qcdV*sf_tt8TeV',topTagSF),
}

for x in ['singlemuontop','singleelectrontop']:
  weights[x] = weights['top']
for x in ['singlemuonw','singleelectronw']:
  weights[x] = weights['w']
for x in ['dimuon','dielectron']:
  weights[x] = weights['notag']
for x in ['photon']:
  weights[x] = tTIMES('sf_pho',weights['notag'])
'''

for r in ['signal','top','w','singlemuontop','singleelectrontop','singlemuonw','singleelectronw']:
  for shift in ['BUp','BDown','MUp','MDown']:
    for cent in ['sf_btag','sf_sjbtag']:
      weights[r+'_'+cent+shift] = sub(cent+'0',cent+'0'+shift,sub(cent+'1',cent+'1'+shift,weights[r]))