import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  SpreadsheetFile,
  Workbook,
} from "file:///C:/Users/usu_compras12/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = path.join(rootDir, "outputs", "modelos");
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const modelo = workbook.worksheets.add("Carga real");
const apoio = workbook.worksheets.add("Apoio");
const instrucoes = workbook.worksheets.add("Instrucoes");

const headers = [
  "tipo_instrumento",
  "status",
  "numero_contrato",
  "numero_aditivo",
  "fornecedor",
  "cnpj",
  "secretaria",
  "secretario",
  "gestor",
  "fiscal",
  "objeto",
  "vigencia_texto",
  "inicio_vigencia",
  "fim_vigencia",
  "data_os",
  "processo_administrativo",
  "processo_execucao",
  "audesp_licitacao",
  "audesp_ajuste",
  "modalidade",
  "valor_total",
  "data_assinatura",
  "data_publicacao",
  "observacao",
];

modelo.getRange("A1:X1").values = [headers];
modelo.getRange("A2:X6").values = Array.from({ length: 5 }, () => Array(headers.length).fill(null));
modelo.getRange("A2:X2").values = [[
  "contrato",
  "ativo",
  "001/2026",
  null,
  "Fornecedor Exemplo Ltda - CNPJ 12.345.678/0001-90",
  "12.345.678/0001-90",
  "Saude",
  "Secretario Exemplo - CPF 123.456.789-00",
  "Gestor Exemplo - CPF 123.456.789-00",
  "Fiscal Exemplo - CPF 123.456.789-00",
  "Objeto do contrato ou ata",
  "01/01/2026 a 31/12/2026",
  new Date("2026-01-01"),
  new Date("2026-12-31"),
  null,
  "PA 123/2026",
  null,
  null,
  null,
  "Pregao eletronico",
  150000,
  new Date("2025-12-20"),
  new Date("2025-12-22"),
  "Linha de exemplo; substitua por dados reais",
]];
modelo.getRange("A1:X1").format = {
  fill: "#134E4A",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
modelo.getRange("A2:X200").format = { wrapText: true };
modelo.getRange("M2:O200").format.numberFormat = "dd/mm/yyyy";
modelo.getRange("V2:W200").format.numberFormat = "dd/mm/yyyy";
modelo.getRange("U2:U200").format.numberFormat = "R$ #,##0.00";
modelo.getRange("A:X").format.columnWidthPx = 150;
modelo.getRange("K:K").format.columnWidthPx = 320;
modelo.getRange("L:L").format.columnWidthPx = 220;
modelo.freezePanes.freezeRows(1);
const table = modelo.tables.add("A1:X200", true, "TabelaCargaContratos");
table.style = "TableStyleMedium2";

apoio.getRange("A1:B1").values = [["Campo", "Valores aceitos / observacao"]];
apoio.getRange("A2:B16").values = [
  ["tipo_instrumento", "contrato ou ata_registro_preco"],
  ["status", "ativo, encerrado, alerta, critico ou outro texto curto"],
  ["numero_contrato", "Obrigatorio para evitar duplicidade"],
  ["fornecedor", "Pode conter nome e CNPJ no mesmo campo"],
  ["cnpj", "Aceita com ou sem pontuacao"],
  ["secretaria", "Nome da secretaria/unidade"],
  ["gestor/fiscal/secretario", "Pode conter CPF no texto; o importador tenta extrair"],
  ["vigencia_texto", "Exemplo: 01/01/2026 a 31/12/2026"],
  ["inicio_vigencia/fim_vigencia", "Preferencialmente dd/mm/aaaa"],
  ["valor_total", "Use numero ou moeda brasileira"],
  ["data_assinatura/data_publicacao", "Preferencialmente dd/mm/aaaa"],
  ["Linhas vazias", "Sao ignoradas"],
  ["Titulos de secao", "Sao ignorados quando nao parecem contrato"],
  ["Aba de importacao", "Use a aba Carga real"],
  ["Formato aceito", "Salve como .xlsx ou .xls"],
];
apoio.getRange("A1:B1").format = {
  fill: "#1F2937",
  font: { bold: true, color: "#FFFFFF" },
};
apoio.getRange("A:B").format.columnWidthPx = 260;
apoio.getRange("B:B").format.columnWidthPx = 420;
apoio.getRange("A1:B16").format = { wrapText: true };
apoio.freezePanes.freezeRows(1);

instrucoes.getRange("A1:D1").values = [["Modelo de importacao de contratos - ARGOS", "", "", ""]];
instrucoes.getRange("A1:D1").merge();
instrucoes.getRange("A3:D10").values = [
  ["1", "Preencha a aba Carga real mantendo os cabecalhos originais.", "", ""],
  ["2", "Apague a linha de exemplo antes de importar, se nao quiser carrega-la.", "", ""],
  ["3", "No sistema, acesse Contratos > Importar Planilha e envie este arquivo.", "", ""],
  ["4", "A base deste ambiente fica zerada, exceto pelo usuario admin criado para login.", "", ""],
  ["5", "Para zerar novamente pelo Docker, pare o ambiente e execute docker compose down -v.", "", ""],
  ["", "", "", ""],
  ["Login inicial", "admin@argos.gov.br", "Senha", "argos123"],
  ["Portas", "Frontend 5175", "API 8002", "Postgres 5434"],
];
instrucoes.getRange("A1:D1").format = {
  fill: "#0F766E",
  font: { bold: true, color: "#FFFFFF", size: 14 },
};
instrucoes.getRange("A3:A10").format = {
  font: { bold: true },
  fill: "#E0F2F1",
};
instrucoes.getRange("A:D").format.columnWidthPx = 220;
instrucoes.getRange("B:B").format.columnWidthPx = 420;
instrucoes.getRange("A1:D10").format = { wrapText: true };

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "scan erros",
});
const preview = await workbook.render({
  sheetName: "Carga real",
  range: "A1:X8",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  path.join(outputDir, "preview_modelo_importacao_contratos_real.png"),
  new Uint8Array(await preview.arrayBuffer()),
);
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const outPath = path.join(outputDir, "modelo_importacao_contratos_real.xlsx");
await xlsx.save(outPath);

console.log(`Modelo gerado: ${outPath}`);
console.log(errors.ndjson || "Nenhum erro de formula encontrado.");
