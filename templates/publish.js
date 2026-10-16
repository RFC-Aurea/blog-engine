async function() {
  // Paste this function unchanged as the ExecuteWixAPI `code`.
  // Pass runs/<run>/compact.json in the `files` bundle as "compact.json".
  const input = JSON.parse(files.find((f) => f.path === "compact.json").content);
  // Fingerprint of the post content, compared with the local compact.json by verify_live.py.
  const fnv = (s) => {
    let h = 2166136261;
    for (const ch of s) {
      h ^= ch.codePointAt(0);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h.toString(16);
  };
  const inputHash = fnv(JSON.stringify(input.draftPost) + JSON.stringify(input.doc));
  const C = input.colors;
  let count = 0;
  const nid = () => "e" + String(++count).padStart(3, "0");
  const runs = (list, color) => list.map((r) => {
    const flags = r[1] || "";
    const link = r[2] || null;
    const d = [];
    if (flags.includes("b")) {
      d.push({ type: "BOLD", fontWeightValue: 700 });
    }
    if (flags.includes("i")) {
      d.push({ type: "ITALIC", italicData: true });
    }
    const c = color || (C.colorBody || link ? C.body : null);
    if (c) {
      d.push({ type: "COLOR", colorData: { foreground: c } });
    }
    if (link) {
      const internal = link.startsWith(C.domain) || link.startsWith("/");
      d.push({ type: "LINK", linkData: { link: { url: link, target: internal ? "SELF" : "BLANK" } } });
      d.push({ type: "UNDERLINE" });
    }
    return { type: "TEXT", id: "", nodes: [], textData: { text: r[0], decorations: d } };
  });
  const para = (list) => ({ type: "PARAGRAPH", id: nid(), nodes: runs(list), paragraphData: {} });
  const spacer = () => ({ type: "PARAGRAPH", id: nid(), nodes: [], paragraphData: {} });
  const nodes = [];
  for (const b of input.doc) {
    const k = b[0];
    if (k === "p") {
      nodes.push(para(b[1]));
    } else if (k === "sp") {
      nodes.push(spacer());
    } else if (k === "h") {
      nodes.push({
        type: "HEADING",
        id: b[2] || nid(),
        nodes: runs(b[4], b[3]),
        headingData: { level: b[1], textStyle: { textAlignment: "AUTO" } }
      });
    } else if (k === "ul" || k === "ol") {
      const items = b[1].map((it) => ({ type: "LIST_ITEM", id: nid(), nodes: [para(it)] }));
      if (k === "ul") {
        nodes.push({ type: "BULLETED_LIST", id: nid(), nodes: items, bulletedListData: { indentation: 0 } });
      } else {
        nodes.push({ type: "ORDERED_LIST", id: nid(), nodes: items, orderedListData: { indentation: 0 } });
      }
    } else if (k === "table") {
      const rows = b[2].map((row, ri) => ({
        type: "TABLE_ROW",
        id: nid(),
        nodes: row.map((cell) => ({
          type: "TABLE_CELL",
          id: nid(),
          nodes: [para(cell)],
          tableCellData: ri === 0 ? { cellStyle: { backgroundColor: C.headerBg } } : {}
        }))
      }));
      nodes.push({
        type: "TABLE",
        id: nid(),
        nodes: rows,
        tableData: {
          dimensions: {
            colsWidthRatio: b[1],
            rowsHeight: rows.map(() => 0),
            colsMinWidth: b[1].map(() => 120)
          },
          rowHeader: true
        }
      });
    } else if (k === "img") {
      nodes.push({
        type: "IMAGE",
        id: nid(),
        nodes: [],
        imageData: {
          containerData: { width: { size: "CONTENT" }, alignment: "CENTER", textWrap: true },
          image: { src: { id: b[1] }, width: b[2], height: b[3] },
          altText: b[4]
        }
      });
    } else if (k === "q") {
      nodes.push({ type: "BLOCKQUOTE", id: nid(), nodes: [para(b[1])], blockquoteData: { indentation: 1 } });
    } else if (k === "toc") {
      nodes.push({
        type: "PARAGRAPH",
        id: nid(),
        paragraphData: {},
        nodes: [{
          type: "TEXT",
          id: "",
          nodes: [],
          textData: {
            text: "In this article",
            decorations: [{ type: "BOLD", fontWeightValue: 700 }, { type: "COLOR", colorData: { foreground: C.tocLabel } }]
          }
        }]
      });
      const items = b[1].map((t) => ({
        type: "LIST_ITEM",
        id: nid(),
        nodes: [{
          type: "PARAGRAPH",
          id: nid(),
          paragraphData: {},
          nodes: [{
            type: "TEXT",
            id: "",
            nodes: [],
            textData: {
              text: t[1],
              decorations: [
                { type: "ANCHOR", anchorData: { anchor: t[0] } },
                { type: "COLOR", colorData: { foreground: C.toc } },
                { type: "UNDERLINE" }
              ]
            }
          }]
        }]
      }));
      nodes.push({ type: "BULLETED_LIST", id: nid(), nodes: items, bulletedListData: { indentation: 0 } });
      nodes.push(spacer());
    } else {
      throw new Error("unknown block " + k);
    }
  }
  const draftPost = Object.assign({}, input.draftPost, { richContent: { nodes: nodes } });
  const body = { draftPost: draftPost, publish: input.publish, fieldsets: ["URL"] };
  if (input.dryRun) {
    return { dryRun: true, body: body, inputHash: inputHash };
  }
  const created = await wix.request({
    method: "POST",
    url: "https://www.wixapis.com/blog/v3/draft-posts",
    body: body
  });
  const draft = created.draftPost;
  let post = null;
  if (input.publish) {
    const got = await wix.request({
      method: "GET",
      url: "https://www.wixapis.com/blog/v3/posts/" + draft.id + "?fieldsets=RICH_CONTENT&fieldsets=SEO&fieldsets=URL"
    });
    post = got.post;
  } else {
    const got = await wix.request({
      method: "GET",
      url: "https://www.wixapis.com/blog/v3/draft-posts/" + draft.id + "?fieldsets=RICH_CONTENT&fieldsets=URL"
    });
    post = got.draftPost;
  }
  const h2 = [];
  const images = [];
  const anchors = [];
  let h3 = 0;
  let links = 0;
  const walk = (list) => {
    for (const n of list || []) {
      if (n.type === "HEADING" && n.headingData.level === 2) {
        h2.push(n.id);
      }
      if (n.type === "HEADING" && n.headingData.level === 3) {
        h3 += 1;
      }
      if (n.type === "IMAGE") {
        images.push(n.imageData.image.src.id);
      }
      if (n.type === "TEXT") {
        for (const d of n.textData.decorations || []) {
          if (d.type === "LINK") {
            links += 1;
          }
          if (d.type === "ANCHOR") {
            anchors.push(d.anchorData.anchor);
          }
        }
      }
      walk(n.nodes);
    }
  };
  walk(post.richContent ? post.richContent.nodes : []);
  const seo = post.seoData || draft.seoData || {};
  return {
    inputHash: inputHash,
    draftId: draft.id,
    postId: post.id,
    status: post.status || null,
    url: post.url ? post.url.base + post.url.path : null,
    slug: post.slug || post.seoSlug,
    title: post.title,
    memberId: post.memberId,
    categoryIds: post.categoryIds,
    h2: h2,
    h3: h3,
    links: links,
    anchors: anchors,
    images: images,
    seoKeywords: seo.settings ? seo.settings.keywords : [],
    seoTagTypes: (seo.tags || []).map((t) => t.type + (t.props ? ":" + (t.props.name || t.props.property || t.props.type || "") : ""))
  };
}
