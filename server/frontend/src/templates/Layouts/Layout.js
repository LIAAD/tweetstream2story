import {Helmet} from "react-helmet";
import Footer from "../Footers/Footer";
import Header from "../Headers/Header";
import favicon from "../../assets/images/favicon.ico"

const Layout = (props) => {
    return (
        <>
            <Helmet>
                <html lang="en"/>
                <title>TweetStream2Story</title>
                <link rel="icon" type="image/png" href={favicon} sizes="16x16"/>
            </Helmet>
            <Helmet>
                <body className="body-background-color"/>
            </Helmet>
            {props.helmet}
            <header>{props.header ?? <Header/>}</header>
            <main>{props.main}</main>
            {props.footers ?? <Footer/>}
        </>
    );
};

export default Layout;
