import {Col, Container, Row} from "react-bootstrap";
import Layout from "../../templates/Layouts/Layout";
import Sidebar from "../../templates/Sidebar/Sidebar";
import Title from "../../templates/Sidebar/Title";

const About = () => {
    return (
        <Layout
            main={
                <Container fluid={true} className="pb-5">
                    <Title title={"About"}/>
                    <Row className="mt-5 mx-2 mx-lg-0 min-vh-70">
                        <Sidebar/>
                        <Col lg={8}
                             className="text-justify enhanced-body-background-color rounded-corners px-4 px-lg-5 py-5">
                            <h1 className={"mb-3"}>TweetStream2Story</h1>
                            <p> The rise of social media has brought a great transformation to the way news are discovered and
                                shared. Unlike traditional news sources, social media allows anyone to cover a story. Therefore,
                                sometimes an event is already discussed by people before a journalist turns it into a news article.
                                Twitter is a particularly appealing social network for discussing events, since its posts are very
                                compact and, therefore, contain colloquial language and abbreviations. However, its large volume
                                of tweets also makes it impossible for a user to keep up with an event.
                            </p>
                            <p>
                                TweetStream2Story is a framework that allows the extraction of narratives from tweets posted
                                in real time, about a topic of choice, by automatically collecting, cleaning and summarizing tweets.
                                The user can visualize the evolution of the topic's narrative through time in different formats, such
                                as a knowledge graph, a list of tweets or an annotation file.
                            </p>
                        </Col>
                    </Row>
                </Container>
            }
        />
    );
};

export default About;
