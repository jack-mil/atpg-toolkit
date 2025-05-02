// From: https://github.com/talal/ilm
//     & https://github.com/mbollmann/typst-kunskap

// Colors used across the template.
#let link-color = rgb("#3282B8")
#let muted-color = luma(160)
#let block-bg-color = luma(240)

#let stroke-color = luma(200)
#let fill-color = luma(250)

// Workaround for the lack of an `std` scope.
#let std-bibliography = bibliography
#let std-smallcaps = smallcaps
#let std-upper = upper

// Overwrite the default `smallcaps` and `upper` functions with increased spacing between
// characters. Default tracking is 0pt.
#let smallcaps(body) = std-smallcaps(text(tracking: 0.6pt, body))
#let upper(body) = std-upper(text(tracking: 0.6pt, body))

// This function gets your whole document as its `body`.
#let ilm(
  // The title for your work.
  title: [Your Title],
  // Author's name.
  author: "Author",
  // The paper size to use.
  paper-size: "us-letter",
  // Date that will be displayed on cover page.
  // The value needs to be of the 'datetime' type.
  // More info: https://typst.app/docs/reference/foundations/datetime/
  // Example: datetime(year: 2024, month: 03, day: 17)
  date: datetime.today(),
  // Format in which the date will be displayed on cover page.
  // More info: https://typst.app/docs/reference/foundations/datetime/#format
  // The default format will display date as: MMMM DD, YYYY
  date-format: "[month repr:long] [day padding:zero], [year repr:full]",
  header: "",
  // Fonts
  body-font: "Noto Serif",
  body-font-size: 12pt,
  raw-font: ("Cascadia Code", "Fira Mono"),
  raw-font-size: 11pt,
  headings-font: ("Noto Serif", "Source Sans 3"),
  margin-font: "Source Sans 3",
  math-font: "Fira Math",
  // An abstract for your work. Can be omitted if you don't have one.
  abstract: none,
  // The contents for the preface page. This will be displayed after the cover page. Can
  // be omitted if you don't have one.
  preface: none,
  // The result of a call to the `outline` function or `none`.
  // Set this to `none`, if you want to disable the table of contents.
  // More info: https://typst.app/docs/reference/model/outline/
  table-of-contents: outline(),
  // Display an appendix after the body but before the bibliography.
  appendix: (
    enabled: false,
    title: "",
    heading-numbering-format: "",
    body: none,
  ),
  // The result of a call to the `bibliography` function or `none`.
  // Example: bibliography("refs.bib")
  // More info: https://typst.app/docs/reference/model/bibliography/
  bibliography: none,
  // Whether to start a chapter on a new page.
  chapter-pagebreak: true,
  // Whether to display a maroon circle next to external links.
  external-link-circle: true,
  // Display an index of figures (images).
  figure-index: (
    enabled: false,
    title: "",
  ),
  // Display an index of tables
  table-index: (
    enabled: false,
    title: "",
  ),
  // Display an index of listings (code blocks).
  listing-index: (
    enabled: false,
    title: "",
  ),
  // The content of your work.
  body,
) = {
  // Set the document's metadata.
  set document(title: title, author: author)

  // Set the body font.
  set text(font: body-font, size: body-font-size)

  // Set raw text font.
  // Default is Fira Mono at 8.8pt
  show raw: set text(font: raw-font, size: raw-font-size)

  show math.equation: set text(font: math-font)

  // Configure page size and margins.
  set page(
    paper: paper-size,
    margin: (bottom: 1.75cm, top: 2.25cm),
  )

  // Set title block
  // {
  //     v(26pt)
  //     text(font: headings-font, weight: "medium", size: 22pt, title)
  //     linebreak()
  //     v(16pt)
  //     if type(author) == array {
  //         text(font: body-font, style: "italic", author.join(", "))
  //     } else {
  //         text(font: body-font, style: "italic", author)
  //     }
  //     if date != none {
  //         v(2pt)
  //         text(font: body-font, date.display(date-format))
  //     }
  //     v(5em)
  // }

  // Cover page.
  page(
    align(
      left + horizon,
      block(width: 90%)[
        #let v-space = v(2em, weak: true)
        #text(3em)[*#title*]

        #v-space
        #text(1.6em, author)

        #if abstract != none {
          v-space
          block(width: 80%)[
            // Default leading is 0.65em.
            #par(leading: 0.78em, justify: true, linebreaks: "optimized", abstract)
          ]
        }

        #if date != none {
          v-space
          text(date.display(date-format))
        }
      ],
    ),
  )

  // Configure paragraph properties.
  // Default leading is 0.65em.
  // Default spacing is 1.2em.
  set par(leading: 0.7em, spacing: 1.35em, justify: true, linebreaks: "optimized")

  show heading: it => {
    // Add vertical space before headings
    if it.level == 1 {
      v(6%, weak: true)
    } else {
      v(4%, weak: true)
    }
    // Set headings font
    set text(font: headings-font, weight: "medium")
    it

    // Add vertical space after headings.
    v(3%, weak: true)
  }
  // Do not hyphenate headings.
  show heading: set text(hyphenate: false)

  show heading.where(level: 3): it => text(
    font: headings-font,
    // size: body-font-size,
    weight: "medium",
    it.body + h(1em),
  )

  // Show a small maroon circle next to external links.
  show link: it => {
    underline(it)
    // Workaround for ctheorems package so that its labels keep the default link styling.
    if external-link-circle and type(it.dest) != label {
      sym.wj
      h(1.6pt)
      sym.wj
      super(box(height: 3.8pt, circle(radius: 1.2pt, stroke: 0.7pt + rgb("#993333"))))
    }
  }

  // Display preface as the second page.
  if preface != none {
    page(preface)
  }

  // Indent nested entries in the outline.
  set outline(indent: auto)

  // Display table of contents.
  if table-of-contents != none {
    table-of-contents
  }


  // Configure page numbering and footer.
  set page(
    header: context {
      if counter(page).get().first() > 1 [
        #set text(font: margin-font, fill: muted-color)
        #header
        #h(1fr)
        #title
      ] else [
        #set text(font: margin-font)
        #header
      ]
    },
    numbering: (..nums) => {
      set text(font: margin-font, fill: muted-color)
      nums.pos().first() - 1
    },
  )

  // Configure page numbering and footer.
  // set page(footer: context {
  //   // Get current page number.
  //   let i = counter(page).at(here()).first()

  //   // Align right for even pages and left for odd.
  //   let is-odd = calc.odd(i)
  //   let aln = right
  //   // let aln = if is-odd {
  //   //   right
  //   // } else {
  //   //   left
  //   // }

  //   // Are we on a page that starts a chapter?
  //   let target = heading.where(level: 1)
  //   if query(target).any(it => it.location().page() == i) {
  //     return align(aln)[#i]
  //   }

  //   // Find the chapter of the section we are currently in.
  //   let before = query(target.before(here()))
  //   if before.len() > 0 {
  //     let current = before.last()
  //     let gap = 1.75em
  //     let chapter = upper(text(size: 0.68em, current.body))
  //     if current.numbering != none {
  //       if is-odd {
  //         align(aln)[#chapter #h(gap) #i]
  //       } else {
  //         align(aln)[#i #h(gap) #chapter]
  //       }
  //     }
  //   }
  // })

  // Configure equation numbering.
  set math.equation(numbering: "(1)")

  // Display inline code in a small box that retains the correct baseline.
  show raw.where(block: false): box.with(
    fill: fill-color.darken(2%),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 2pt,
  )

  // Display block code with padding and shaded background
  show raw.where(block: true): block.with(
    inset: (x: 1.5em, y: 5pt),
    outset: (x: -1em),
    width: 100%,
    fill: block-bg-color,
    stroke: stroke-color,
  )

  // Break large tables across pages.
  show figure.where(kind: table): set block(breakable: true)
  show figure: set figure.caption(position: top)
  set table(
    // Increase the table cell's padding
    inset: 5pt, // default is 5pt
    stroke: (0.5pt + stroke-color),
    fill: (_, y) => if calc.odd(y) {
      block-bg-color
    },
  )
  // Use smallcaps for table header row.
  // show table.cell.where(y: 0): smallcaps
  show table.cell: set text(11pt)

  // Wrap `body` in curly braces so that it has its own context. This way show/set rules
  // will only apply to body.
  {
    // Configure heading numbering.
    // set heading(numbering: "1.")

    // Start chapters on a new page.
    show heading.where(level: 1): it => {
      if chapter-pagebreak {
        pagebreak(weak: true)
      }
      it
    }
    body
  }

  // Display appendix before the bibliography.
  if appendix.enabled {
    // pagebreak()
    // heading(level: 1)[#appendix.at("title", default: "Appendix")]
    page(
      align(
        center + horizon,
        block(width: 90%)[
          #heading(level: 1)[#text(size: 2em)[#appendix.at("title", default: "Appendix")]]
        ],
      ),
    )

    // For heading prefixes in the appendix, the standard convention is A.1.1.
    let num-fmt = appendix.at("heading-numbering-format", default: "A.1.1.")

    counter(heading).update(0)
    set heading(
      outlined: true,
      numbering: (..nums) => {
        let vals = nums.pos()
        if vals.len() > 0 {
          let v = vals.slice(0)
          return numbering(num-fmt, ..v)
        }
      },
    )

    appendix.body
  }

  // Display bibliography.
  if bibliography != none {
    pagebreak()
    show std-bibliography: set text(0.85em)
    // Use default paragraph properties for bibliography.
    show std-bibliography: set par(leading: 0.65em, justify: false, linebreaks: auto)
    bibliography
  }

  // Display indices of figures, tables, and listings.
  let fig-t(kind) = figure.where(kind: kind)
  let has-fig(kind) = counter(fig-t(kind)).get().at(0) > 0
  if figure-index.enabled or table-index.enabled or listing-index.enabled {
    show outline: set heading(outlined: true)
    context {
      let imgs = figure-index.enabled and has-fig(image)
      let tbls = table-index.enabled and has-fig(table)
      let lsts = listing-index.enabled and has-fig(raw)
      if imgs or tbls or lsts {
        // Note that we pagebreak only once instead of each each individual index. This is
        // because for documents that only have a couple of figures, starting each index
        // on new page would result in superfluous whitespace.
        pagebreak()
      }

      if imgs {
        outline(
          title: figure-index.at("title", default: "Index of Figures"),
          target: fig-t(image),
        )
      }
      if tbls {
        outline(
          title: table-index.at("title", default: "Index of Tables"),
          target: fig-t(table),
        )
      }
      if lsts {
        outline(
          title: listing-index.at("title", default: "Index of Listings"),
          target: fig-t(raw),
        )
      }
    }
  }
}

// This function formats its `body` (content) into a blockquote.
#let blockquote(body) = {
  block(
    width: 100%,
    fill: fill-color,
    inset: 2em,
    stroke: (y: 0.5pt + stroke-color),
    body,
  )
}
