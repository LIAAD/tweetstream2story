import { useEffect, useState } from 'react'
import { VerticalTimeline, VerticalTimelineElement } from 'react-vertical-timeline-component';
import { Button, ButtonGroup, Dropdown, DropdownButton, Row } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import TableTweets from '../Tables/TableTweets';
import DRSGraph from "../Tabs/DRSGraph";
import TableAnnotations from '../Tables/TableAnnotations';
import TableEvents from '../Tables/TableEvents';
import ModalGraph from '../Modals/ModalGraph';

const NarrativeTimeline = (props) => {

    const [selectedWindow, setWindow] = useState(0)
    return (
        <VerticalTimeline layout={'1-column-left'}>
            {props.windows.map((window, index) => (
                <Narrative
                    key={index}
                    handleSelect={() => setWindow(index)}
                    selected={selectedWindow === index}
                    window={window}
                    window_index={index}
                    mode={props.mode}
                    lang={props.topic.lang}
                    id={props.topic.es_id}
                />

            ))}
        </VerticalTimeline>
    );
};

const Narrative = (props) => {

    useEffect(() => {
        if (props.selected) {
            getTweets();
        }
    }, []);

    const [showGraph, setShowGraph] = useState(false);

    const [intervalTweets, setIntervalTweets] = useState({});
    const [globalTweets, setGlobalTweets] = useState({});

    const [loading, setLoading] = useState(false);

    const [selectedOption, setSelectedOption] = useState('1');
    const options = [
        { name: 'Knowledge Graph', value: '1' },
        { name: 'Tweets', value: '2' },
        { name: 'Actors', value: '3' }
    ];

    const [technicalMode, setTechnicalMode] = useState(false);
    const [selectedTechnical, setSelectedTechnical] = useState('0');
    const technicalOptions = [
        { name: 'Annotations', value: '0' },
        { name: 'DRS', value: '1' },
    ]

    const formatDatetime = (datetime) => {
        // Convert from ISO to local and then to YYYY-MM-DD hh:mm
        datetime = new Date(datetime);
        let dd = datetime.getDate(); // day of the month
        let MM = datetime.getMonth() + 1; // getMonth() is zero-based
        let hh = datetime.getHours();
        let mm = datetime.getMinutes();

        return [datetime.getFullYear(), '-',
        (MM > 9 ? '' : '0') + MM, '-',
        (dd > 9 ? '' : '0') + dd,
            ' ',
        (hh > 9 ? '' : '0') + hh, ':',
        (mm > 9 ? '' : '0') + mm
        ].join('');
    }

    const getTweets = () => {

        setLoading(true);

        const headers = new Headers({
            "Authorization": "Bearer " + localStorage.getItem("session"),
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
        });
        
        return fetch(
            `${process.env.REACT_APP_API_URL}/api/topic/${props.id}/window/${props.window_index}/tweets`,
            {
                method: "GET",
                headers: headers,
            }
        )
            .then((r) => r.json())
            .then((r) => {
                setGlobalTweets(r.tweets.global_tweets);
                setIntervalTweets(r.tweets.interval_tweets)
                setLoading(false);
            })
            .catch((e) => {
                console.error(e);
                setLoading(false);
            });
    }

    const visualizationSwitch = (narrative) => {

        if (!technicalMode) {
            if (selectedOption === '1')
                return (
                    <>
                        {Object.keys(narrative).length === 0
                            ? <div>Couldn't extract narrative for this set of tweets</div>
                            : <>
                                <Button
                                    variant={"light-blue"}
                                    style={{ zIndex: 2, position: "absolute" }}
                                    onClick={() => setShowGraph(true)}>
                                    <FontAwesomeIcon icon="fas fa-expand-alt" />
                                </Button>
                                <DRSGraph
                                    actors_dict={narrative.actors_dict}
                                    events_dict={narrative.events_dict}
                                    ann_str={narrative.ann_str}
                                    event_relations={narrative.event_relations}
                                    non_event_relations={narrative.non_event_relations}
                                    new_actors={narrative.new_actors} />

                            </>
                        }
                    </>
                );
            if (selectedOption === '2')
                return (
                    <TableTweets tweets={props.mode === '1' ? globalTweets : intervalTweets} />
                );

            if (selectedOption === '3')
                return (
                    <>
                        {Object.keys(narrative).length === 0
                            ? <div>Couldn't extract narrative for this set of tweets</div>
                            : <ul>
                                {Object.keys(narrative.actors_dict).map((term, index) => (
                                    <li key={index} as="button">
                                        {narrative.actors_dict[term]}
                                    </li>
                                ))}
                            </ul>
                        }
                    </>
                )

        } else {
            if (selectedTechnical === '0') {
                return (
                    <>
                        {Object.keys(narrative).length !== 0 &&
                            <TableAnnotations ann_str={narrative.ann_str} />
                        }
                    </>
                );
            }

            if (selectedTechnical === '1') {
                return (
                    <>
                        {Object.keys(narrative).length !== 0 &&
                            <TableEvents drs_str={narrative.drs_str} />
                        }
                    </>
                )
            }
        }
    }

    return (
        <VerticalTimelineElement
            className="vertical-timeline-element--work"
            contentStyle={{
                padding: '1px 10px',
                display: props.selected ? 'block' : 'inline-block',
            }}
            contentArrowStyle={{
                borderRight: '7px solid white',
            }}
            date={formatDatetime(props.window.start_time)}
            iconStyle={{
                width: '10px',
                height: '10px',
                left: '15px',
                top: '18px',
                background: 'rgb(33, 150, 243)',
                color: '#fff',
                boxShadow: '0 0 0 2px #fff,inset 0 2px 0 rgba(0,0,0,.08),0 3px 0 4px rgba(0,0,0,.05)',
                cursor: 'pointer'
            }}
            iconOnClick={() => { props.handleSelect(); getTweets(); }}
        >
            {props.selected &&
                <>
                    <Row className="mb-3">
                        <ButtonGroup>
                            {options.map((option, index) => (
                                <Button
                                    key={index}
                                    id={`visualization-${index}`}
                                    type="radio"
                                    name="visualization"
                                    variant={((!technicalMode) && (selectedOption === option.value)) ? 'light-blue' : 'outline-light-blue'}
                                    value={option.value}
                                    checked={selectedOption === option.value}
                                    onChange={(e) => { setTechnicalMode(false); setSelectedOption(e.currentTarget.value); }}
                                    onClick={() => { setTechnicalMode(false); setSelectedOption(option.value); }}
                                    style={{ minWidth: "150px" }}
                                >
                                    {option.name}
                                </Button>
                            ))}
                            <DropdownButton
                                id="dropdown-item-button"
                                title={technicalMode ? technicalOptions[selectedTechnical].name : "Technical"}
                                variant={technicalMode ? 'light-blue' : 'outline-light-blue'}
                                as={ButtonGroup}>
                                
                                {technicalOptions.map((option, index) => (
                                    <Dropdown.Item
                                        key={index}
                                        as="button"
                                        onClick={() => { setTechnicalMode(true); setSelectedTechnical(option.value) }}
                                        variant={selectedTechnical === option ? 'light-blue' : 'outline-light-blue'}
                                        style={{ width: "150px" }}>
                                        {option.name}
                                    </Dropdown.Item>
                                ))}
                            </DropdownButton>
                        </ButtonGroup>
                    </Row>

                    {props.mode === '1' &&
                        <>
                            {visualizationSwitch(props.window.global_narrative)}
                        </>
                    }
                    {props.mode === '2' &&
                        <>
                            {visualizationSwitch(props.window.interval_narrative)}
                        </>
                    }
                </>
            }
            <ModalGraph results={props.window.global_narrative} show={showGraph} setShow={setShowGraph} />

        </VerticalTimelineElement>
    )


}


export default NarrativeTimeline;
