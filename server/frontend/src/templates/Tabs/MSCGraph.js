import { renderMsc } from "mscgenjs";
import { useEffect } from "react";

const MSCGraph = (props) => {
  useEffect(() => {
    const example_str = `msc {
        # options - separate with , end with ;
        #
        # arcgradient=20, # slopes the arcs.
        # hscale="0.8", # horizontally squeezes or stretches the chart
        # width="600", # sets the maximum width of the chart (pixels).
        #              # xù and msgenny also allow the value 'auto' - it scales
        #              # rendered svg's to maximum available width.
        # watermark="a watermark", # adds a watermark (xù only!)
        wordwraparcs=on; # automatically wrap labels on arcs. Default: off
      
        # entities
        #
        # possible attributes
        #   label
        #   textcolor, textbgcolor, linecolor # as advertised
        #
        # these color the arcs departing from the entity:
        #   arctextcolor, arctextbgcolor, arclinecolor
        #
      
        cust [label="Customer"],
        shop,
        "delivery service",
        bank;
      
        # arcs
        #
        # attributes:
        #   label, textcolor, textbgcolor, linecolor # as advertised
        #   arcskip # arc starts here, ends the specified amount
        #           # of lines lower.
        #           # use e.g. arcskip="1" to end on the next line.
        #
        # arc types: ->, =>, =>>, >>, -x, :>,
        #            <->, <=>, <<=>>, <<>>, <:>
        #            --, ::, ..
        #            note, box, abox, rbox
      
        cust => shop [label="order(thing)"];
        shop -> "delivery service" [label="deliver(thing)"];
        "delivery service" =>> cust [label="thing"];
        cust >> "delivery service" [label="OK"];
      
        "delivery service" => shop [label="delivered!"];
        shop => cust [label="bill"];
        cust => bank [label="pay(bill, shop)"];
        bank => shop [label="€"];
      
        # inline expressions (xù only):
        # xù only  : alt, else, opt, break, critical,
        #            neg, strict, seq, assert, exc
        #            ref, consider, ignore, loop, par
        #
        # # e.g. to describe to alternatives :
        # shop alt bank [label="payment OK"]{
        #
        #   shop =>> bank [label="Thanks dude!"];
        #
        #   --- [label="payment NOK"]; # split alternatives with ---
        #
        #   shop =>> bank [label="that was not enough :-("];
        #   bank >> shop [label="Sorry. Bye."];
        #   shop rbox shop [label="payment pending process"];
        # };
      }
      `;

    renderMsc(example_str, { elementId: "msc" });
  }, []);

  return <pre id="msc" className="mscgen_js" />;
};

export default MSCGraph;
