import {getSession} from "next-auth/react"
import clientPromise from "../../../lib/mongodb";
import {ObjectId} from "mongodb";

export default async function handler(req, res) {
    const session = await getSession({req})
    if (!session) return res.json({success: false});
    const mongoClient = await clientPromise;
    const db = mongoClient.db();
    // db.collection()
    console.log(session)
    const account = await db.collection("accounts").findOne({userId: ObjectId(session.user._id)})

    const { platform } = req.query;
    if (platform == null) {
        // idfk what to do
    } else {
        await db.collection("accounts").updateOne(account, { $set: { targetRTMPUri: platform }}, {});
    }

    res.json({account, rtmp: `rtmp://anony.news:1935/${account.userId}/akfjlagi2`});
}
