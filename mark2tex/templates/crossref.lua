-- crossref.lua — referências cruzadas + legenda ABNT para mark2tex
--
-- REFERÊNCIAS CRUZADAS
--   @fig:id  →  Figura~\ref{fig:id}
--   @tbl:id  →  Tabela~\ref{tbl:id}
--   Demais @citacoes passam ao BibTeX normalmente.
--
-- FIGURAS (ordem ABNT: legenda acima, fonte abaixo)
--   ![Legenda](img/fig.png){#fig:id fonte="o autor (2026)" width=90%}
--
--   Gera:
--     \begin{figure}[H]
--     \centering
--     \caption{Legenda}       ← acima da imagem
--     \label{fig:id}
--     \includegraphics[...]{img/fig.png}
--     {\footnotesize Fonte: o autor (2026).}   ← abaixo da imagem
--     \end{figure}

-- ── Referências cruzadas ────────────────────────────────────────────────────
function Cite(el)
  if FORMAT ~= 'latex' then return el end
  if #el.citations ~= 1 then return el end
  local id = el.citations[1].id
  local fig = id:match('^fig:(.+)$')
  if fig then
    return pandoc.RawInline('latex', 'Figura~\\ref{fig:' .. fig .. '}')
  end
  local tbl = id:match('^tbl:(.+)$')
  if tbl then
    return pandoc.RawInline('latex', 'Tabela~\\ref{tbl:' .. tbl .. '}')
  end
  return el
end

-- ── Figuras: legenda acima + fonte abaixo ───────────────────────────────────
function Figure(fig)
  if FORMAT ~= 'latex' then return fig end

  -- Identificador do Figure (ex.: "fig:rtsp")
  local img_id = (fig.identifier ~= '') and fig.identifier or nil

  -- Atributos podem estar no Figure ou na Image interna.
  -- Em pandoc 3.x os atributos do bloco {#id key=val} ficam no Figure;
  -- mas em algumas versões ficam na Image — checamos os dois.
  local fonte = fig.attr.attributes['fonte']
  local width = fig.attr.attributes['width']

  -- Percorre fig.content (lista de Blocks) procurando a Image
  local img_src = nil
  for _, blk in ipairs(fig.content) do
    local inlines = nil
    if     blk.t == 'Plain' then inlines = blk.content
    elseif blk.t == 'Para'  then inlines = blk.content
    end
    if inlines then
      for _, il in ipairs(inlines) do
        if il.t == 'Image' then
          img_src = il.src
          -- Fallback: atributos na Image interna
          if not fonte and il.attr and il.attr.attributes then
            fonte = il.attr.attributes['fonte']
          end
          if not width and il.attr and il.attr.attributes then
            width = il.attr.attributes['width']
          end
          -- Fallback: id na Image
          if not img_id and il.identifier and il.identifier ~= '' then
            img_id = il.identifier
          end
          break
        end
      end
    end
    if img_src then break end
  end

  if not img_src then return fig end

  -- Extrai os inlines da primeira linha da legenda
  local cap_inlines = {}
  if #fig.caption.long > 0 then
    local first = fig.caption.long[1]
    if first.t == 'Plain' or first.t == 'Para' then
      cap_inlines = first.content
    end
  end

  -- Converte os inlines para LaTeX (preserva negrito, itálico, \texttt, etc.)
  local cap_latex = ''
  if #cap_inlines > 0 then
    cap_latex = pandoc.write(
      pandoc.Pandoc({ pandoc.Plain(cap_inlines) }), 'latex')
    cap_latex = cap_latex:gsub('%s*\n*$', '')
  end

  -- Opção de largura para \includegraphics (ex.: 90% → [width=0.90\textwidth])
  local width_opt = ''
  if width then
    local pct = width:match('^(%d+)%%?$')
    if pct then
      width_opt = string.format('[width=%.2f\\textwidth]', tonumber(pct) / 100)
    end
  end

  -- Monta o ambiente figure com a ordem correta pela ABNT
  local lines = { '\\begin{figure}[H]', '\\centering' }

  if cap_latex ~= '' then
    table.insert(lines, '\\caption{' .. cap_latex .. '}')
  end
  if img_id and img_id ~= '' then
    table.insert(lines, '\\label{' .. img_id .. '}')
  end

  table.insert(lines, '\\includegraphics' .. width_opt .. '{' .. img_src .. '}')

  if fonte then
    table.insert(lines, '\\par{\\footnotesize Fonte: ' .. fonte .. '.}')
  end

  table.insert(lines, '\\end{figure}')

  return pandoc.RawBlock('latex', table.concat(lines, '\n'))
end
