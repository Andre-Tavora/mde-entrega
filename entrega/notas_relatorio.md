## Melhoria identificada: fusao de nos gemeos (alias_map)
- 8 titulos duplicados (7 artefatos de migracao 47xx<->67xx, 1 sobreposicao legitima: acao penal)
- 47 questoes com tema central em no duplicado: 46 revisar, 1 publicar (Q0112, gemeo nos extras)
- 28/46 na faixa [thr-0.10, thr), tipicamente conf=0.80 (4/5 votos, provavel voto dividido com o gemeo)
- Ganho estimado de cobertura com fusao pre-votacao: ate +28 questoes (~7.8 p.p.)
- NAO aplicado nesta entrega: evita contaminar a auditoria do holdout; exige reauditoria das promovidas
- Producao 50k: canonicalizar alias antes do self-consistency
