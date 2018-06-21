#include "../interface/L1Mod.h"

using namespace pa; 
using namespace std; 

void L1Mod::execute() 
{
  gt.runNumber = event.run;
  gt.lumiNumber = event.lumi;
  gt.eventNumber = event.event; 
  gt.met = event.met_p4->pt();
  gt.metphi = event.met_p4->phi();

  gt.nJot = event.jet_p4->size(); 
  for (int iJ = 0; iJ != min((int)gt.nJot, NL1JET); ++iJ) {
    auto& jet = (*(event.jet_p4))[iJ];
    gt.jotPt[iJ] = jet.pt(); 
    gt.jotPhi[iJ] = jet.phi(); 
    gt.jotEta[iJ] = jet.eta(); 
    gt.jotE[iJ] = jet.e();
    gt.jotNEMF[iJ] = (*(event.jet_neutralEmFrac))[iJ]; 
    gt.jotNHF[iJ] = (*(event.jet_neutralHadFrac))[iJ]; 
    if (gt.jotPt[iJ] > 30) {
      gt.mindphi = min(gt.mindphi, (float)SignedDeltaPhi(gt.jotPhi[iJ], gt.metphi));
      for (int iTP = 0; iTP != (int)event.L1EG_bx->size(); ++iTP) {
        auto& tp = (*(event.L1EG_p4))[iTP]; 
        if (tp.pt() < 30) 
          continue; 
        int iso = (*(event.L1EG_iso))[iTP];
        if (DeltaR2(jet.eta(), jet.phi(), tp.eta(), tp.phi()) < 0.16) { 
          int bx = (*(event.L1EG_bx))[iTP];
          if (bx < gt.jotL1EGBX[iJ]) {
            gt.jotL1Pt[iJ] = tp.pt();
            gt.jotL1Eta[iJ] = tp.eta();
            gt.jotL1Phi[iJ] = tp.phi(); 
            gt.jotL1E[iJ] = tp.e();
            gt.jotL1EGBX[iJ] = bx;
            gt.jotL1EGIso[iJ] = iso;
          }
        }
      }
    }
  }
  if (gt.nJot > 1) {
    gt.jot12DEta = gt.jotEta[0] - gt.jotEta[1];
    gt.jot12DPhi = SignedDeltaPhi(gt.jotPhi[0], gt.jotPhi[1]);
    gt.jot12Mass = ((*(event.jet_p4))[0] + (*(event.jet_p4))[1]).mass();
  }
}