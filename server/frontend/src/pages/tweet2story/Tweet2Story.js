import { useState, useEffect } from "react";
import { Button, Col, Container, Form, Row, Spinner } from "react-bootstrap";
import Layout from "../../templates/Layouts/Layout";
import Sidebar from "../../templates/Sidebar/Sidebar";
import Title from "../../templates/Sidebar/Title";
import TableTopics from "../../templates/Tables/TableTopics"
import ModalRealTime from "../../templates/Modals/ModalRealTime";

const Tweet2Story = (props) => {

    const [query, setQuery] = useState("");
    const [topics, setTopics] = useState([]);
    const [loadingTopics, setLoadingTopics] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [formError, setFormError] = useState("")

    // Retrieve data when loading component
    useEffect(() => {

        // Get active topics to display in table
        getTopics();

    }, []);

    const getTopics = () => {
        const headers = new Headers({
           "Authorization": "Bearer " + localStorage.getItem("session"),
        });
        setLoadingTopics(true);
        fetch(`${process.env.REACT_APP_API_URL}/api/topics/`,
            {
                headers: headers
            })
            .then(r => r.json())
            .then(r => {
                setLoadingTopics(false);
                setTopics(r.topics);
            })
            .catch(e => console.error(e));
    }

    const startTopic = (id) => {
        const headers = new Headers({
            "Authorization": "Bearer " + localStorage.getItem("session"),
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
        });
        setLoadingTopics(true);
        fetch(`${process.env.REACT_APP_API_URL}/api/start_topic/`,
            {
                method: "POST",
                headers: headers,
                body: JSON.stringify({ es_id: id })
            })
            .then(r => getTopics())
            .catch(e => console.error(e));
    }

    const stopTopic = (id) => {

        const headers = new Headers({
            "Authorization": "Bearer " + localStorage.getItem("session"),
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
        });

        setLoadingTopics(true);
        fetch(`${process.env.REACT_APP_API_URL}/api/stop_topic/`,
            {
                method: "POST",
                headers: headers,
                body: JSON.stringify({ es_id: id })
            })
            .then(r => getTopics())
            .catch(e => console.error(e));
    }
    const deleteTopic = (id) => {

        const headers = new Headers({
            "Authorization": "Bearer " + localStorage.getItem("session"),
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
        });
        setLoadingTopics(true);
        fetch(`${process.env.REACT_APP_API_URL}/api/delete_topic/`,
            {
                method: "DELETE",
                headers: headers,
                body: JSON.stringify({ es_id: id })
            })
            .then(r => getTopics())
            .catch(e => console.error(e));
    }

    const handleSubmit = (topic) => {
        const headers = new Headers({
                "Authorization": "Bearer " + localStorage.getItem("session"),
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
        });
        fetch(`${process.env.REACT_APP_API_URL}/api/topic/`,
            {
                method: "POST",
                headers: headers,
                body: JSON.stringify({...topic, "query": query}),
            })
            .then(r => {
                
                if (r.ok) {
                    setShowModal(false);
                    setLoadingTopics(true);
                    getTopics();
                } else {
                    if (r.status === 403) {
                        console.log("a")
                        setFormError("Invalid Twitter API Credentials")
                    }
                }
            })
            .catch((e) => {
                console.error(e);
                setLoadingTopics(false);
            });
        
    }

    return (
        <Layout
            main={
                <Container fluid={true} className="pb-5">
                    <Title title={"Try it Out"} />
                    <Row className="mt-5 mx-3 mx-lg-0 min-vh-70">
                        <Sidebar />
                        <Col lg={9} className="rounded-corners enhanced-body-background-color px-4 pe-lg-5 pt-4 pb-5">
                            <Form className="mb-5" onSubmit={event => { event.preventDefault(); setShowModal(true); }} >
                                <Form.Group className="mb-3">
                                    <Row className="align-items-center mb-3">
                                        <Col lg={6} className="font-lg mb-lg-0 mb-4">
                                            <Form.Label>Tell me about...</Form.Label>
                                        </Col>
                                    </Row>
                                    <Row>
                                        <Col className="ms-lg-2 me-lg-5">
                                            <>
                                                {!fetching && (
                                                    <Form.Control
                                                        type="text"
                                                        placeholder="Type your query"
                                                        rows={10}
                                                        name="text"
                                                        value={query}
                                                        onChange={(event) => setQuery(event.target.value)}
                                                    />
                                                )}
                                                {fetching && (
                                                    <>
                                                        <Spinner animation="border" />
                                                        <span className="ms-2">Loading</span>
                                                    </>
                                                )}
                                            </>
                                        </Col>
                                    </Row>
                                </Form.Group>
                                {!fetching && (
                                    <>
                                        <Row>
                                            <Col className="text-end">
                                                <Button variant="outline-dark" type="submit" disabled={query===""}>
                                                    Extract Narrative
                                                </Button>
                                            </Col>
                                        </Row>
                                    </>
                                )}
                            </Form>
                            <hr />
                            <Row>
                                <Col>
                                    <h4>My Topics</h4>
                                    <> 
                                        {!loadingTopics && (
                                            <TableTopics
                                                topics={topics}
                                                startCallback={startTopic}
                                                stopCallback={stopTopic}
                                                deleteCallback={deleteTopic}
                                                editable={true}
                                            />
                                        )}
                                        {loadingTopics && (
                                            <>
                                                <Spinner animation="border" />
                                                <span className="ms-2">Loading</span>
                                            </>
                                        )}
                                    </>
                                </Col>
                            </Row>
                        </Col>
                    </Row>
                    <ModalRealTime submitCallback={handleSubmit} setShowModal={setShowModal} show={showModal} error={formError}/>
                </Container>
            }
        />
    );
};

export default Tweet2Story;
