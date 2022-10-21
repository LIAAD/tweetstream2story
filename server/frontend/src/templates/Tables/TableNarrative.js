import { useState } from "react";
import { Button, Table } from "react-bootstrap";
import ModalTweets from "../Modals/ModalTweets"
import ModalGraph from "../Modals/ModalGraph";
import ModalAnnotations from "../Modals/ModalAnnotations";
import ModalEvents from "../Modals/ModalEvents";


const TableNarrative = (props) => {

    return (
        <div>
            <Table striped bordered hover>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Narrative</th>
                        {/*<th>Clean tweets</th>*/}
                    </tr>
                </thead>
                <tbody>
                    {props.results.map((result, index) => (
                        <Row key={index} result={result} index={index}></Row>
                    ))}
                </tbody>
            </Table>
        </div>
        
    )
};

const Row = (props) => {

    //const [collapsed, setCollapsed] = useState(true);
    const [showTweetsModal, setShowTweetsModal] = useState(false);
    const [showGraph, setShowGraph] = useState(false);
    const [showAnnotations, setShowAnnotations] = useState(false);
    const [showEvents, setShowEvents] = useState(false);

    const [values, setValues] = useState({
        text: props.result.results.map(tweet => tweet._source.clean_text).slice(0,20).join("\n"),
        lang: "pt",
        tools: {
            'spaCy': true,
            'NLTK': true,
            'AllenNLP': true,
            'py_heideltime': true,
            //'Spark NLP': true
            'Spacy (Objectal Linking)': true,
            'AllenNLP (Sematic Role Labeling)': true,
        }      
    })
    const [results, setResults] = useState({});
    
    const formatDatetime = (datetime) => {
        // Convert from ISO to local and then to YYYY-MM-DD hh:mm
        datetime = new Date(datetime);
        let dd = datetime.getDate(); // day of the month
        let MM = datetime.getMonth() + 1; // getMonth() is zero-based
        let hh = datetime.getHours();
        let mm = datetime.getMinutes();

        return  [datetime.getFullYear(), '-',
        (MM>9 ? '' : '0') + MM, '-' ,
        (dd>9 ? '' : '0') + dd,
        ' ',
        (hh>9 ? '' : '0') + hh, ':',
        (mm>9 ? '' : '0') + mm
        ].join('');
    }

    const createKnowledgeGraph = () => {

        if (Object.keys(results).length !== 0) {
            setShowGraph(true);
            return;
        }

        const header = new Headers();

        header.append("Content-Type", "application/json");
        header.append("Access-Control-Allow-Origin", "*");
        header.append("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

        setResults({});

        fetch(
            `${process.env.REACT_APP_API_URL}/api/demo/`,
            {
                method: "POST",
                headers: header,
                body: JSON.stringify({...values}),
            }
        )
            .then((r) => r.json())
            .then((r) => {
                setResults(r);
                setShowGraph(true);  

            })
            .catch((e) => {
                console.error(e);
            });
    }

    const createAnnotations = () => {

        if (Object.keys(results).length !== 0) {
            setShowAnnotations(true);
            return;
        }
        
        const header = new Headers();

        header.append("Content-Type", "application/json");
        header.append("Access-Control-Allow-Origin", "*");
        header.append("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

        setResults({});

        fetch(
            `${process.env.REACT_APP_API_URL}/api/demo/`,
            {
                method: "POST",
                headers: header,
                body: JSON.stringify({...values}),
            }
        )
            .then((r) => r.json())
            .then((r) => {
                setResults(r);
                setShowAnnotations(true);  

            })
            .catch((e) => {
                console.error(e);
            });   
    }

    const createEvents = () => {

        if (Object.keys(results).length !== 0) {
            setShowEvents(true);
            return;
        }
        
        const header = new Headers();

        header.append("Content-Type", "application/json");
        header.append("Access-Control-Allow-Origin", "*");
        header.append("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

        setResults({});

        fetch(
            `${process.env.REACT_APP_API_URL}/api/demo/`,
            {
                method: "POST",
                headers: header,
                body: JSON.stringify({...values}),
            }
        )
            .then((r) => r.json())
            .then((r) => {
                setResults(r);
                setShowEvents(true);  

            })
            .catch((e) => {
                console.error(e);
            });   
    }

    return (
        <tr>
            <ModalTweets tweets={props.result.results} setShow={setShowTweetsModal} show={showTweetsModal}/>
            <ModalGraph results={results} show={showGraph} setShow={setShowGraph}/>
            <ModalAnnotations results={results} show={showAnnotations} setShow={setShowAnnotations}/>
            <ModalEvents results={results} show={showEvents} setShow={setShowEvents}/>

            <td>{formatDatetime(props.result.start_time)}</td>
            <td>
                {/*
                <FontAwesomeIcon icon="fa-solid fa-angle-down" onClick={() => setCollapsed(!collapsed)}/>
                /*
                {!collapsed &&
                    <>
                        <img alt="oi" src="https://media.discordapp.net/attachments/798270349737328680/977986864579498004/unknown.png?width=732&height=574"/>
                        <ul>
                            {props.result.results.map((tweet, index) => (
                                <li key={index}>
                                    {tweet._source.text}
                                </li>
                        ))}
                        </ul>
                    </>
                }
                */}
                <Button variant="outline-dark" onClick={() => setShowTweetsModal(true)}>
                    Tweets
                </Button>

                <Button variant="outline-dark" onClick={() => createKnowledgeGraph()}>
                    Knowledge Graph
                </Button>

                <Button variant="outline-dark" onClick={() => createAnnotations()}>
                    Annotations
                </Button>

                <Button variant="outline-dark" onClick={() => createEvents()}>
                    Events
                </Button>
            </td>
        </tr>
    )
}

export default TableNarrative;
//
/*
{(!topic.active && !topic.finished) &&
    <Button variant="success" onClick={() => {props.startCallback(topic.es_id)}}>
        <FontAwesomeIcon icon="fas fa-play"/> Start
    </Button>
}
*/

/*
        
        */