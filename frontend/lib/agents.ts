export interface AgentMetadata {
    id: string;
    name: string;
    description: string;
    themeColor: string;
    icon: string;
    gradient: string;
    demoUrl: string;
}

export const AGENTS: AgentMetadata[] = [
    {
        id: "1",
        name: "The Assistant",
        description: "A helpful voice assistant for general queries and tasks.",
        themeColor: "blue",
        icon: "🤖",
        gradient: "from-blue-500 to-cyan-400",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_10daysofvoiceagents-murfai-voicetech-activity-7398018435697430528-uiCb"
    },
    {
        id: "2",
        name: "Barista Bot",
        description: "Order your favorite coffee with a friendly AI barista.",
        themeColor: "amber",
        icon: "☕",
        gradient: "from-amber-500 to-orange-400",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_murfaivoiceagentschallenge-10daysofai-voicetech-activity-7398381954691186688-xe8n"
    },
    {
        id: "3",
        name: "Wellness Companion",
        description: "A calming presence for meditation and mental health check-ins.",
        themeColor: "emerald",
        icon: "🧘",
        gradient: "from-emerald-500 to-teal-400",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_murfaivoiceagentschallenge-10daysofaivoiceagents-activity-7398734410298114048-za00"
    },
    {
        id: "4",
        name: "Polyglot Tutor",
        description: "Practice languages with a patient and knowledgeable tutor.",
        themeColor: "violet",
        icon: "📚",
        gradient: "from-violet-500 to-purple-400",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_day4-murfaivoiceagentschallenge-murfai-activity-7399068606942326784-L1BF"
    },
    {
        id: "5",
        name: "Sales Rep (SDR)",
        description: "A persuasive sales development representative for mock calls.",
        themeColor: "indigo",
        icon: "💼",
        gradient: "from-indigo-500 to-blue-600",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_day5-murfaivoiceagentschallenge-10daysofaivoiceagents-activity-7399433477181489152-xVfM"
    },
    {
        id: "6",
        name: "Fraud Detective",
        description: "Report suspicious activity to a vigilant security agent.",
        themeColor: "red",
        icon: "🕵️",
        gradient: "from-red-500 to-rose-600",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_murfai-fraudalert-murfaivoiceagentchallenge-activity-7399791498340294656-iJlK"
    },
    {
        id: "7",
        name: "Foodie Friend",
        description: "Get restaurant recommendations and discuss culinary delights.",
        themeColor: "orange",
        icon: "🍔",
        gradient: "from-orange-500 to-yellow-400",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_10daysofaivoiceagents-murfai-murffalcon-activity-7400088582235029505-Daq9"
    },
    {
        id: "8",
        name: "Dungeon Master",
        description: "Embark on a fantasy text-adventure guided by a storyteller.",
        themeColor: "purple",
        icon: "🐉",
        gradient: "from-purple-600 to-fuchsia-500",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_10daysofaivoiceagents-murfai-murffalcon-activity-7400532501397635073-S-Nt"
    },
    {
        id: "9",
        name: "Shop Assistant",
        description: "Find the perfect product with a helpful e-commerce guide.",
        themeColor: "pink",
        icon: "🛍️",
        gradient: "from-pink-500 to-rose-400",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_murfai-murffalcon-murfaivoiceagentschallenge-activity-7400903944450920450-TgSy"
    },
    {
        id: "10",
        name: "Improv Host",
        description: "Test your wit in a fast-paced improv comedy battle!",
        themeColor: "yellow",
        icon: "🎤",
        gradient: "from-yellow-400 to-amber-300",
        demoUrl: "https://www.linkedin.com/posts/ashishsinghbhadauriya_murfaivoiceagentschallenge-10daysofaivoiceagents-activity-7401282950643970048-F8DH"
    }
];

export function getAgent(id: string) {
    return AGENTS.find(a => a.id === id);
}
