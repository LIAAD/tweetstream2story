import { useState } from "react";
import Graph from "react-vis-network-graph";

const DRSGraph = (props) => {

        let graph
        let options
        const [physicsEnabled, setPhysicsEnabled]= useState(true)
        const events = {
            stabilized: (event) => {
                
                console.log("stabilized")
                return setPhysicsEnabled(false);
            }
        }

        const nodes = []
        const edges = []

        const nodes_dict = {} // key = label, value = id of node
        const actors_nodes = {} // key = id of actor, value = label

        const actors_in_relations = [];
        let nodes_count = 0

        // Each unique actor is a node
        for (const [key, value] of Object.entries(props.actors_dict)){
            
            if (!(value in nodes_dict)) {
                nodes_dict[value] = nodes_count;
                let node = {id: nodes_count, label: value}
                if (props.new_actors.includes(value)) {
                    node.color = "#ffea73"
                }
                nodes.push(node);
                nodes_count += 1;
            }

            actors_nodes[key] = nodes_dict[value]
        }
        console.log("RELATIONS")

        // 2 cases:
        // [T1, theme, E2]; [T3, theme, E2]
        // = T1 ---T2---> T3

        // [T1, theme, E2]; [E3, theme, E2]; [T4, theme, E3]
        // = T1 ----E2+E3---> T4
        for (let i = 0; i < props.non_event_relations.length - 1; i = i + 2) {
            const origin = props.non_event_relations[i];
            const next = props.non_event_relations[i+1];

            if (origin[2] !== next[2]) {
                //console.error("The Relation origin and dest don't match")
                i--;
                continue
            }

            if (origin[0] === next[0]) {
                i--;
                continue;
            }

            const line = props.ann_str.filter((line) => line.includes(`${origin[2]} EVENT:`))
            if (line.length === 0) {
                console.error("The corresponding line in the ann_text was not found");
                return;
            }

            // Case 1 (relation with 2 actors, 1 event)
            if (next[0][0] === 'T') {
                const dest = next;
                const event_token_id = line[0].split(':')[1]

                const event = props.events_dict[event_token_id];
                actors_in_relations.push(actors_nodes[origin[0]], actors_nodes[dest[0]]);
                edges.push({
                    from: actors_nodes[origin[0]],
                    to: actors_nodes[dest[0]],
                    label: `${event} (${origin[1]})`}
                )
                console.log(`${props.actors_dict[origin[0]]} ${event} ${props.actors_dict[dest[0]]}`)
            }

            // Case 2 (relation with 2 actors, 2 events)
            // e.g. Tavira ---- (temos o ar impregnado) + (do) -----> incêndio
            if (next[0][0] === 'E') {
                const dest = props.non_event_relations[i+2];
                if (!dest) {
                    continue;
                }
                i+=1; // Skip one more line

                const line2 = props.ann_str.filter((line) => line.includes(`${dest[2]} EVENT:`))
                if (line2.length === 0) {
                    console.error("The corresponding line in the ann_text was not found");
                    return;
                }

                const event1_token_id = line[0].split(':')[1]
                const event2_token_id = line2[0].split(':')[1]
                const event1 = props.events_dict[event1_token_id];
                const event2 = props.events_dict[event2_token_id];

                actors_in_relations.push(actors_nodes[origin[0]], actors_nodes[dest[0]]);
                edges.push({
                    from: actors_nodes[origin[0]],
                    to: actors_nodes[dest[0]],
                    label: `${event1} ${event2} (${origin[1]})`}
                )
                console.log(`${props.actors_dict[origin[0]]} ${event1} ${event2} ${props.actors_dict[dest[0]]}`)
            }
        }

        props.event_relations.forEach((element) =>
            edges.push({from: element[0], to: element[2], label: element[1]})
        );
        
        console.log("ACTORS")
        nodes.forEach(node => {

            if (! actors_in_relations.includes(node.id))
                console.log(node.label)
        });

        graph = {
            nodes: nodes,
            edges: edges,
        };
        options = {
            autoResize: true,
            height: '300px',
            width: '100%',
            locale: 'pt',
            clickToUse: false,
            
            layout: {
                randomSeed: 3000,
                improvedLayout: true,
            },
            physics: {
                enabled: physicsEnabled,
                solver: 'forceAtlas2Based',
                /*
                barnesHut: {
                    theta: 0,
                    gravitationalConstant: 0,
                    centralGravity: 0,
                    springLength: 0,
                    springConstant: 0,
                    damping: 0,
                    avoidOverlap: 1
                },*/
                forceAtlas2Based: {
                    avoidOverlap: 0.5,
                    centralGravity: 0.01,
                    gravitationalConstant: -20
                },
                stabilization: {
                    'iterations': 10000,
                }
            },
        }
        return (
            <Graph graph={graph} options={options} events={events}
            />
        )
    }
;

export default DRSGraph;
