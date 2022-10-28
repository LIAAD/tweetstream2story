import { useState, useEffect } from "react";
import { Col, Container, Row, Spinner } from "react-bootstrap";
import Layout from "../../templates/Layouts/Layout";
import Sidebar from "../../templates/Sidebar/Sidebar";
import Title from "../../templates/Sidebar/Title";
import { useParams } from "react-router-dom";
import IntervalSwitch from "../../templates/Switchs/IntervalSwitch";

import 'react-vertical-timeline-component/style.min.css';
import NarrativeTimeline from "../../templates/Timelines/NarrativeTimeline";

const Topic = (props) => {

    // Elasticsearch index name
    let { id } = useParams();

    const [topic, setTopic] = useState({});
    const [loadingTopic, setLoadingTopic] = useState(true);

    // '1': Global, '2': By interval
    const [mode, setMode] = useState('1')

    // Retrieve data when loading component
    useEffect(() => {

        // Get active topics to display in table
        getTopic();

    }, []);

    const getTopic = () => {

        setLoadingTopic(true);
        const headers = new Headers({
            "Authorization": "Bearer " + localStorage.getItem("session"),
        });
        
        fetch(`${process.env.REACT_APP_API_URL}/api/topic/${id}`,
            {
                headers: headers
            })
            .then(r => r.json())
            .then(r => {
                setTopic(r.topic);
                setLoadingTopic(false);
            })
            .catch(e => console.error(e));
    }

    return (
        <Layout
            main={
                <Container fluid={true} className="pb-5">
                    <Title title={topic.tag} />
                    <Row className="mt-5 mx-3 mx-lg-0 min-vh-70">
                        <Sidebar />
                        <Col lg={9} className="rounded-corners enhanced-body-background-color px-4 pe-lg-5 pt-4 pb-5">

                            <Row>
                                <Col className="text-end ms-auto">
                                    <IntervalSwitch mode={mode} handleSelect={(mode) => setMode(mode)} />
                                </Col>
                            </Row>

                            {!loadingTopic && (
                                <NarrativeTimeline mode={mode} topic={topic} windows={topic.time_windows}>
                                </NarrativeTimeline>
                            )}

                            {loadingTopic && (
                                <>
                                    <Spinner animation="border" />
                                    <span className="ms-2">Loading</span>
                                </>
                            )}


                        </Col>
                    </Row>
                </Container>
            }
        />
    );
};

export default Topic;
