import {useMemo, useState} from "react";
import {Button} from "react-bootstrap";

const ButtonSample = (props) => {
    const [name, setName] = useState("");

    const handleClick = (e) => {
        e.preventDefault();
        let value = "";
        let lang = ""
        switch (props.title) {
            case "en-1":
                value = "A missile strike on a transmission tower in northern Ukraine has killed at least nine people and left nine more injured, a local official has said.\n" +
                    "\n" +
                    "Vitaliy Koval, the governor of the Rivne region, said the tower and a nearby administrative building were hit by two separate missiles in the attack which took place in the village of Antopi.\n" +
                    "\n" +
                    "\"There are still people under the rubble,\" he added. Local media reported terrestrial TV and radio broadcasts were off air in Ukraine's northern Rivne region after the strike this morning."
                lang = 'en'
                props.setChecked(false)
                break;

            case "en-2":
                value = "Liverpool are trying to sign Colombia winger Luis Diaz from Porto in the current transfer window.\n" +
                    "\n" +
                    "The deal, if completed, is expected to be worth €45m (£37.5m) plus a maximum of €15m in potential bonuses.\n" +
                    "\n" +
                    "Liverpool were planning to wait until the summer but changed their stance as it became clear that Diaz could move elsewhere if they did not act.\n" +
                    "\n" +
                    "The 25-year-old had been linked with a move to Tottenham, who reportedly had a bid of around £38m rejected.\n" +
                    "\n" +
                    "Diaz was Liverpool boss Jurgen Klopp's first choice for the summer when the asking price would have been €60 million (£49.9m).";
                lang = 'en'
                props.setChecked(false)
                break;

            case "en-3":
                value = "The new Formula 1 season is only a week away - but can it match the drama and controversy of 2021 and that final race, in which Max Verstappen snatched the title from Lewis Hamilton?\n" +
                    "\n" +
                    "The fallout has barely subsided during the three-month off-season, with the removal of race director Michael Masi, question marks over seven-time champion Hamilton's future, and an ongoing rivalry between Red Bull team principal Christian Horner and Mercedes counterpart Toto Wolff.\n" +
                    "\n" +
                    "And now the fourth series of Drive to Survive - the hit all-access Netflix documentary about F1 - is streaming, taking us behind the scenes of last year's epic championship battle, which was decided on the final day of the season by a controversial call and a one-lap shootout.\n" +
                    "\n" +
                    "Among the many accusations in the aftermath of that thrilling Abu Dhabi Grand Prix was the claim it had been engineered for maximum entertainment - sacrificing sporting integrity for TV drama.\n" +
                    "\n" +
                    "But, speaking to BBC Sport, the producers of Drive to Survive said there was simply no way decisions were made with Netflix in mind.";
                lang = 'en'
                props.setChecked(false)
                break;

            case "pt-1":
                value = "Desde o dia 14 de Janeiro, data em que podiam começar a ser pagos os vales de viagens não usados na pandemia, até ao dia 22 de Fevereiro, o Turismo de Portugal recebeu 2245 pedidos de intervenção da comissão arbitral que decide o accionamento do Fundo de Garantia de Viagens e Turismo (FGVT).\n" +
                    "\n" +
                    "Destes, de acordo com fonte oficial do Turismo de Portugal (que recebe os requerimentos e preside à comissão), 2085 dizem respeito a viagens de finalistas, dos quais 1804 da Xtravel, 248 da Orgulhojovem, 26 da Sporjovem e sete da SlideIn. Já houve uma decisão relativa a 40 processos, dos quais 21 ligados a viagens de finalistas, mas desconhece-se o seu sentido.";
                lang = 'pt'
                props.setChecked(true)
                break;

            case "pt-2":
                value = "Em Portugal, um relatório do Instituto Superior Técnico dizia, na semana passada, que a pandemia está a “agravar-se de forma significativa” em Portugal, com o índice de transmissibilidade — R(t) — a subir para 1,09, o que poderá resultar numa sexta vaga de infecções.\n" +
                    "\n" +
                    "Eric Topol escreveu há dias um artigo sobre o perigo de se achar que a pandemia estava terminada e de serem levantadas todas as medidas de prevenção. “Mas não esperava que a nova vaga se manifestasse tão cedo”, disse no Twitter.\n" +
                    "\n" +
                    "A subida está a acontecer cerca de um mês depois de vários países europeus levantarem as maiores restrições ainda em vigor para dificultar a transmissão do vírus que provoca a covid-19, diz o professor Bruce Y. Lee, da Universidade da Cidade de Nova Iorque, num artigo na revista Forbes.";
                lang = 'pt'
                props.setChecked(true)
                break;

            case "pt-3":
                value = "O procurador Orlando Figueira, condenado a seis anos e oito meses de cadeia no final de 2018 por ter sido corrompido pelo ex-vice-presidente de Angola Manuel Vicente no âmbito da Operação Fizz, está há três anos a receber do Ministério da Justiça um salário mensal bruto de 5600 euros, sem estar a trabalhar.\n" +
                    "\n" +
                    "Tal resulta do facto de o procedimento disciplinar que visa o magistrado se arrastar há seis anos, porque o Ministério Público optou por ficar a aguardar o desfecho do processo-crime e só em Dezembro passado, após a confirmação da condenação pelo Tribunal da Relação de Lisboa, avançou com a acusação, que propõe a demissão de Orlando Figueira, a pena disciplinar mais pesada das magistraturas.\n" +
                    "\n" +
                    "A data da acusação foi confirmada ao PÚBLICO pela Procuradoria-Geral da República (PGR), que indicou igualmente o índice salarial aplicado ao procurador, que corresponde a um salário bruto mensal de mais de 5600 euros. Estes significarão cerca de 3500 euros líquidos, segundo o próprio Orlando Figueira afirmou ao PÚBLICO em 2019, quando terminou a licença sem vencimento que gozava desde Setembro de 2012 e decidiu voltar ao Ministério Público.";
                lang = 'pt'
                props.setChecked(true)
                break;

            default:
                break;
        }
        props.setValues({
            ...props.values,
            text: value,
            lang: lang,
        });
    };
    useMemo(() => {
        switch (props.title) {
            case "en-1":
                setName("English Sample 1");
                break;

            case "en-2":
                setName("English Sample 2");
                break;

            case "en-3":
                setName("English Sample 3");
                break;

            case "pt-1":
                setName("Portuguese Sample 1");
                break;

            case "pt-2":
                setName("Portuguese Sample 2");
                break;

            case "pt-3":
                setName("Portuguese Sample 3");
                break;

            default:
                break;
        }
    }, [props.title]);

    return (
        <Button variant="dark" onClick={handleClick}>
            {name}
        </Button>
    );
};
export default ButtonSample;
